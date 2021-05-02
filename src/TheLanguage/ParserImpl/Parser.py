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

from concurrent.futures import Future
from typing import Callable, cast, Dict, Generator, Iterable, List, Optional, Tuple, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

from Error import Error
from Normalize import Normalize
from NormalizedIterator import NormalizedIterator

from ParseGenerator import (
    Node,
    Observer as ParseGeneratorObserverBase,
    Parse as ParseGenerator,
    RootNode
)

from Statement import Statement


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
        statement: Statement,
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        "Observer.ImportInfo",              # Statement represents an import
    ]:
        """Called as content is parsed; return False to terminate parsing for all files"""
        raise Exception("Abstract method")


# ----------------------------------------------------------------------
def Parse(
    fully_qualified_names: List[str],
    observer: Observer,
) -> Union[
    Dict[str, RootNode],
    List[Exception],
]:
    """BugBug"""

    # ----------------------------------------------------------------------
    @dataclass
    class SourceInfo(object):
        Node: RootNode
        Statements: List[Statement]

    # ----------------------------------------------------------------------
    @dataclass
    class ThreadInfo(object):
        pending_ctr: int

        is_terminated: bool                             = False

        source_lookup: Dict[str, SourceInfo]            = {}
        source_pending: Dict[str, List[Iterable]]       = {}

        errors: List[Exception]                         = []

    # ----------------------------------------------------------------------

    thread_info = ThreadInfo(len(fully_qualified_names))
    thread_info_lock = threading.Lock()

    is_complete = threading.Event()

    # ----------------------------------------------------------------------
    class ParseGeneratorObserver(ParseGeneratorObserverBase):
        # ----------------------------------------------------------------------
        def __init__(self):
            self.iter                       = None      # This will be set after the iterator is created

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def Enqueue(funcs):
            return observer.Enqueue(funcs)

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def OnIndent():
            return observer.OnIndent()

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        def OnDedent():
            return observer.OnDedent()

        # ----------------------------------------------------------------------
        @Interface.override
        def OnStatementComplete(self, statement, node, iter_before, iter_after):
            result = observer.OnStatementComplete(statement, node, iter_before, iter_after)

            if isinstance(result, bool):
                if result:
                    return ParseGeneratorObserverBase.OnStatementCompleteFlag.Continue
                else:
                    return ParseGeneratorObserverBase.OnStatementCompleteFlag.Terminate

            elif isinstance(result, Observer.ImportInfo):
                if not result.FullyQualifiedName:
                    raise UnknownSourceError(
                        iter_before.Line,
                        iter_before.Column,
                        result.SourceName,
                    )

                with thread_info_lock:
                    source_info = thread_info.source_lookup.get(result.FullyQualifiedName, None)
                    if source_info is not None:
                        return source_info.Statements

                    assert self.iter
                    thread_info.source_pending.setdefault(result.FullyQualifiedName, []).append(self.iter)

                    thread_info.pending_ctr += 1

                    observer.Enqueue([lambda: Runner(LoadGenerator(result.FullyQualifiedName))])

                    return ParseGeneratorObserverBase.OnStatementCompleteFlag.Yield

            else:
                assert False, result

    # ----------------------------------------------------------------------
    def LoadGenerator(
        fully_qualified_name: str,
    ) -> Generator[
        bool,                               # True to continue, False to terminate
        None,
        Tuple[str, Optional[RootNode]],
    ]:
        # ----------------------------------------------------------------------
        def OnComplete():
            with thread_info_lock:
                assert thread_info.pending_ctr
                thread_info.pending_ctr -= 1

                if thread_info.pending_ctr == 0:
                    is_complete.set()

        # ----------------------------------------------------------------------

        with CallOnExit(OnComplete):
            try:
                normalized_content = Normalize(observer.LoadContent(fully_qualified_name))
                parse_generator_observer = ParseGeneratorObserver()

                iter = ParseGenerator(
                    normalized_content,
                    NormalizedIterator(normalized_content),
                    parse_generator_observer,
                )

                parse_generator_observer.iter = iter

                while True:
                    try:
                        yield next(iter)

                    except StopIteration as ex:
                        return (fully_qualified_name, ex.value)

            except Exception as ex:
                # Add the source file to the exception
                assert not hasattr(ex, "Source")
                setattr(ex, "Source", fully_qualified_name)

                with thread_info_lock:
                    thread_info.errors.append(ex)

                return (fully_qualified_name, None)

    # ----------------------------------------------------------------------
    def Runner(iterator):
        try:
            result = next(iterator)
            assert isinstance(result, bool), result

            with thread_info_lock:
                if not result:
                    thread_info.is_terminated = True

                if thread_info.is_terminated:
                    return

            assert result
            observer.Enqueue([lambda: Runner(iterator)])

        except StopIteration as ex:
            result = ex.value

            with thread_info_lock:
                if thread_info.is_terminated:
                    return

                if isinstance(result, list):
                    thread_info.errors += result

                elif isinstance(result, tuple):
                    fully_qualified_name, root_node = cast(tuple, result)

                    if root_node and fully_qualified_name not in thread_info.source_lookup:
                        thread_info.source_lookup[fully_qualified_name] = SourceInfo(root_node)

                        pending_iterables = thread_info.source_pending.pop(fully_qualified_name, None)
                        if pending_iterables is not None:
                            observer.Enqueue([lambda: Runner(iterable) for iterable in pending_iterables])

                else:
                    assert False, result

    # ----------------------------------------------------------------------

    # Load all content
    observer.Enqueue(
        [
            lambda: Runner(LoadGenerator(fully_qualified_name))
            for fully_qualified_name in fully_qualified_names
        ],
    )

    # Wait for all content to be completed
    is_complete.wait()

    assert not thread_info.source_pending, thread_info.source_pending

    if thread_info.errors:
        return thread_info.errors

    return {fqn: si.Node for fqn, si in thread_info.source_lookup.items()}
