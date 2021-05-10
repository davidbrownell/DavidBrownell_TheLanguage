# ----------------------------------------------------------------------
# |
# |  Parser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-27 07:29:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality to Parse files"""

import os
import threading
import traceback

from concurrent.futures import Future
from typing import Any, Callable, cast, Coroutine, Dict, Generator, Iterable, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface
from CommonEnvironment.SelfGenerator import SelfGenerator

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Coroutine
    from .Error import Error
    from .Normalize import Normalize
    from .NormalizedIterator import NormalizedIterator

    from .ParseGenerator import (
        DynamicStatementInfo,
        Node,
        Observer as ParseGeneratorObserverBase,
        Parse as ParseGenerator,
        RootNode
    )

    from .Statement import Statement


# BugBug: Check for import cycles

# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UnknownSourceError(Error):
    SourceName: str

    MessageTemplate                         = Interface.DerivedProperty("'{SourceName}' could not be found")


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ImportInfo(object):
        SourceName: str
        FullyQualifiedName: Optional[str]   # None if the source name cannot be resolved

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def LoadContent(
        fully_qualified_name: str,
    ):
        """Returns the content associated with the fully qualified name"""
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enqueue(
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        """Enqueues a list of functions to be executed; the Generator will yield immediately after this call"""
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnIndent():
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnDedent():
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnStatementComplete(
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue, False to terminate
        DynamicStatementInfo,
    ]:
        """Called as content is parsed; return False to terminate parsing for all files"""
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ExtractDynamicStatementInfo(
        fully_qualified_name: str,
        node: RootNode
    ) -> DynamicStatementInfo:
        """Extracts statements from a parsed node"""
        raise Exception("Abstract method")


# ----------------------------------------------------------------------
def Parse(
    fully_qualified_names: List[str],
    initial_statement_info: DynamicStatementInfo,
    observer: Observer,
) -> Union[
    Dict[str, RootNode],
    List[Exception],
]:
    """Parses multiple pieces of content"""

    # ----------------------------------------------------------------------
    @dataclass
    class SourceInfo(object):
        Node: RootNode
        SourceInfo: DynamicStatementInfo

    # ----------------------------------------------------------------------
    @dataclass
    class ThreadInfo(object):
        pending_ctr: int

        source_lookup: Dict[str, Optional[SourceInfo]]
        source_pending: Dict[str, List[Iterable]]
        iterator_map: Dict[Any, str]

        errors: List[Exception]

        is_terminated: bool

    # ----------------------------------------------------------------------

    thread_info = ThreadInfo(len(fully_qualified_names), {}, {}, {}, [], False)
    thread_info_lock = threading.Lock()

    is_complete = threading.Event()

    # ----------------------------------------------------------------------
    class ParseGeneratorObserver(ParseGeneratorObserverBase):
        # ----------------------------------------------------------------------
        def __init__(self):
            self.iterator                   = None      # This will be set after the observer is created

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def OnIndent():
            return observer.OnIndent()

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def OnDedent():
            return observer.OnIndent()

        # ----------------------------------------------------------------------
        @Interface.override
        def OnStatementComplete(self, node, iter_before, iter_after):
            result = observer.OnStatementComplete(node, iter_before, iter_after)

            if isinstance(result, bool):
                if result:
                    return Coroutine.Status.Continue

                return Coroutine.Status.Terminate

            elif isinstance(result, Observer.ImportInfo):
                if not result.FullyQualifiedName:
                    raise UnknownSourceError(
                        iter_before.Line,
                        iter_before.Column,
                        result.SourceName,
                    )

                enqueue_import = False

                with thread_info_lock:
                    source_info = thread_info.source_lookup.get(result.FullyQualifiedName, None)
                    if source_info is not None:
                        return cast(SourceInfo, source_info).SourceInfo

                    # Enqueue this iterator for completion after the new one has been loaded
                    thread_info.source_pending.setdefault(result.FullyQualifiedName, []).append(self.iterator)

                    if result.FullyQualifiedName not in thread_info.source_lookup:
                        thread_info.source_lookup[result.FullyQualifiedName] = None
                        thread_info.pending_ctr += 1

                        enqueue_import = True

                if enqueue_import:
                    observer.Enqueue([lambda: Runner(CreateIterator(result.FullyQualifiedName))])

                return Coroutine.Status.Yield

            else:
                assert False, result

    # ----------------------------------------------------------------------
    def CreateIterator(fully_qualified_name):
        parse_generator_observer = ParseGeneratorObserver()

        iterator = ParseGenerator(
            NormalizedIterator(
                Normalize(
                    observer.LoadContent(fully_qualified_name),
                ),
            ),
            initial_statement_info,
            parse_generator_observer,
        )

        parse_generator_observer.iterator = iterator

        with thread_info_lock:
            thread_info.iterator_map[id(iterator)] = fully_qualified_name

        return iterator

    # ----------------------------------------------------------------------
    def Runner(iterator):
        is_iterator_complete = True

        # ----------------------------------------------------------------------
        def OnComplete():
            nonlocal is_iterator_complete

            if not is_iterator_complete:
                return

            with thread_info_lock:
                assert thread_info.pending_ctr
                thread_info.pending_ctr -= 1

                if thread_info.pending_ctr == 0:
                    is_complete.set()

        # ----------------------------------------------------------------------

        with CallOnExit(OnComplete):
            try:
                try:
                    result = next(iterator)

                    with thread_info_lock:
                        if result == Coroutine.Status.Terminate:
                            thread_info.is_terminated = True

                        if thread_info.is_terminated:
                            return

                    is_iterator_complete = False

                    if result == Coroutine.Status.Continue:
                        observer.Enqueue([lambda: Runner(iterator)])

                    elif result == Coroutine.Status.Yield:
                        # Nothing to enqueue, this iterator will continue once the yield item
                        # is complete
                        pass

                    else:
                        assert False, result

                except StopIteration as ex:
                    result = ex.value

                    with thread_info_lock:
                        if thread_info.is_terminated:
                            return

                        assert result

                        fully_qualified_name = thread_info.iterator_map.pop(id(iterator))

                        if thread_info.source_lookup.get(fully_qualified_name, None) is None:
                            dynamic_statement_info = observer.ExtractDynamicStatementInfo(fully_qualified_name, result)

                            # Commit the results
                            thread_info.source_lookup[fully_qualified_name] = SourceInfo(result, dynamic_statement_info)

                            # Should we continue to execute other iterators now that this one has completed?
                            pending_iterators = thread_info.source_pending.pop(fully_qualified_name, None)
                            if pending_iterators is not None:
                                new_funcs = []

                                for pending_iterator in pending_iterators:
                                    pending_iterator.send(dynamic_statement_info)
                                    new_funcs.append(lambda pending_iterator=pending_iterator: Runner(pending_iterator))

                                observer.Enqueue(new_funcs)

            except Exception as ex:
                assert not hasattr(ex, "Traceback")
                object.__setattr__(ex, "Traceback", traceback.format_exc())

                with thread_info_lock:
                    fully_qualified_name = thread_info.iterator_map.pop(id(iterator))

                    assert not hasattr(ex, "Source")
                    object.__setattr__(ex, "Source", fully_qualified_name)

                    thread_info.errors.append(ex)

    # ----------------------------------------------------------------------

    # Load all the content
    observer.Enqueue(
        [
            lambda fully_qualified_name=fully_qualified_name: Runner(CreateIterator(fully_qualified_name))
            for fully_qualified_name in fully_qualified_names
        ],
    )

    # Wait for all content to be completed
    is_complete.wait()

    assert not thread_info.iterator_map, thread_info.iterator_map
    assert not thread_info.source_pending, thread_info.source_pending

    if thread_info.errors:
        return thread_info.errors

    return {fqn: si.Node for fqn, si in thread_info.source_lookup.items()}
