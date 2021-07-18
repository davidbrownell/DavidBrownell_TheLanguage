# ----------------------------------------------------------------------
# |
# |  TranslationUnitsParser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-02 11:23:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality to parse multiple translation units simultaneously"""

import asyncio
import os
import threading
import traceback

from concurrent.futures import Future
from typing import Any, Awaitable, Callable, cast, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .AST import Leaf, Node, RootNode
    from .Error import Error
    from .Normalize import Normalize
    from .NormalizedIterator import NormalizedIterator

    from .Statements.Statement import Statement

    from .TranslationUnitParser import (
        DynamicStatementInfo,
        Observer as TranslationUnitObserver,
        ParseAsync as TranslationUnitParseAsync,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UnknownSourceError(Error):
    SourceName: str

    MessageTemplate                         = Interface.DerivedProperty("'{SourceName}' could not be found")


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ImportInfo(object):
        SourceName: str
        FullyQualifiedName: Optional[str]   # None if the SourceName cannot be resolved

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enqueue(
        funcs: List[Callable[[], None]],
    ) -> List[Future]:
        """Enqueues the funcs for execution on a thread pool"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def LoadContent(
        fully_qualified_name: str,
    ) -> str:
        """Returns the content associated with the fully qualified name"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ExtractDynamicStatements(
        fully_qualified_name: str,
        node: RootNode,
    ) -> DynamicStatementInfo:
        """Extracts statements from parsed content"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnIndentAsync(
        fully_qualified_name: str,
        data_stack: List[Statement.StandardParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Optional[DynamicStatementInfo]:
        """Event generated on the creation of a new scope"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnDedentAsync(
        fully_qualified_name: str,
        data_stack: List[Statement.StandardParseResultData],
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> None:
        """Event generated on the end of a scope"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnStatementCompleteAsync(
        fully_qualified_name: str,
        statement: Statement,
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicStatementInfo,               # DynamicStatementInfo generated by the statement
        "Observer.ImportInfo",              # Import information generated by the statement
    ]:
        """Called on the completion of each statement"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
async def ParseAsync(
    fully_qualified_names: List[str],
    initial_statement_info: DynamicStatementInfo,
    observer: Observer,
    single_threaded=False,
) -> Union[
    None,
    Dict[str, RootNode],
    List[Exception],
]:
    # ----------------------------------------------------------------------
    class SourceInfo(object):
        # ----------------------------------------------------------------------
        def __init__(
            self,
            node: Optional[RootNode],
            statement_info: DynamicStatementInfo,
        ):
            self.Node                       = node
            self.StatementInfo              = statement_info

    # ----------------------------------------------------------------------
    class ThreadInfo(object):
        def __init__(self):
            self.pending_ctr                                                = 0

            self.source_lookup: Dict[str, Optional[SourceInfo]]             = {}
            self.source_pending: Dict[str, List[threading.Event]]           = {}

            self.errors: List[Exception]                                    = []

    # ----------------------------------------------------------------------

    thread_info = ThreadInfo()
    thread_info_lock = threading.Lock()

    is_complete = threading.Event()

    # ----------------------------------------------------------------------
    async def ExecuteAsync(
        fully_qualified_name,
        increment_pending_ctr=True,
    ) -> Optional[DynamicStatementInfo]:
        final_result = None

        # ----------------------------------------------------------------------
        def OnExit():
            nonlocal final_result

            with thread_info_lock:
                final_result = thread_info.source_lookup.get(fully_qualified_name, None)
                if final_result is None:
                    del thread_info.source_lookup[fully_qualified_name]

                    final_result = SourceInfo(None, DynamicStatementInfo((), (), ()))

                for event in thread_info.source_pending.pop(fully_qualified_name, []):
                    event.set()

                if thread_info.pending_ctr == 0:
                    is_complete.set()

        # ----------------------------------------------------------------------

        with CallOnExit(OnExit):
            with thread_info_lock:
                if fully_qualified_name not in thread_info.source_lookup:
                    should_execute = True
                    wait_event = None

                    thread_info.source_lookup[fully_qualified_name] = None

                    if increment_pending_ctr:
                        thread_info.pending_ctr += 1

                else:
                    source_info = thread_info.source_lookup[fully_qualified_name]
                    if source_info is not None:
                        return source_info.StatementInfo

                    should_execute = False
                    wait_event = threading.Event()

                    thread_info.source_pending.setdefault(fully_qualified_name, []).append(wait_event)

            if should_execute:
                # ----------------------------------------------------------------------
                def OnExecuteExit():
                    with thread_info_lock:
                        assert thread_info.pending_ctr
                        thread_info.pending_ctr -= 1

                # ----------------------------------------------------------------------

                with CallOnExit(OnExecuteExit):
                    try:
                        translation_unit_observer = _TranslationUnitObserver(fully_qualified_name, observer, ExecuteAsync)

                        content = observer.LoadContent(fully_qualified_name)

                        root = await TranslationUnitParseAsync(
                            initial_statement_info,
                            NormalizedIterator(Normalize(content)),
                            translation_unit_observer,
                            single_threaded=single_threaded,
                        )

                        if root is None:
                            return None

                        # Get the Dynamic Statements
                        dynamic_statements = observer.ExtractDynamicStatements(fully_qualified_name, root)

                        # Commit the results
                        with thread_info_lock:
                            assert thread_info.source_lookup[fully_qualified_name] is None
                            thread_info.source_lookup[fully_qualified_name] = SourceInfo(root, dynamic_statements)

                    except Exception as ex:
                        assert not hasattr(ex, "Traceback")
                        object.__setattr__(ex, "Traceback", traceback.format_exc())

                        assert not hasattr(ex, "FullyQualifiedName")
                        object.__setattr__(ex, "FullyQualifiedName", fully_qualified_name)

                        with thread_info_lock:
                            thread_info.errors.append(ex)

            elif wait_event:
                wait_event.wait()

        assert final_result
        return final_result.StatementInfo

    # ----------------------------------------------------------------------
    def PrepLoopAndExecute(
        fully_qualified_name,
        increment_pending_ctr=True,
    ):
        thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_loop)

        try:
            return thread_loop.run_until_complete(
                ExecuteAsync(
                    fully_qualified_name,
                    increment_pending_ctr=increment_pending_ctr,
                ),
            )
        finally:
            thread_loop.close()

    # ----------------------------------------------------------------------

    with thread_info_lock:
        # Prepopulate `pending_ctr` so that we can make sure that we don't
        # prematurely terminate as threads are spinning up.
        thread_info.pending_ctr = len(fully_qualified_names)

    if single_threaded:
        for fqn in fully_qualified_names:
            result = await ExecuteAsync(fqn, increment_pending_ctr=False)
            if result is None:
                return None

    else:
        futures = observer.Enqueue(
            [
                cast(Callable[[], None], lambda fqn=fqn: PrepLoopAndExecute(fqn, increment_pending_ctr=False))
                for fqn in fully_qualified_names
            ],
        )

        for future in futures:
            result = future.result()
            if result is None:
                return None

        is_complete.wait()

    assert not thread_info.source_pending, thread_info.source_pending

    if thread_info.errors:
        return thread_info.errors

    return {
        fqn: cast(RootNode, cast(SourceInfo, si).Node)
        for fqn, si in thread_info.source_lookup.items()
    }


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _TranslationUnitObserver(TranslationUnitObserver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        fully_qualified_name: str,
        observer: Observer,
        async_parse_func: Callable[[str], Awaitable[Optional[DynamicStatementInfo]]],
    ):
        self._fully_qualified_name          = fully_qualified_name
        self._observer                      = observer
        self._async_parse_func              = async_parse_func

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnIndentAsync(self, *args, **kwargs):
        return await self._observer.OnIndentAsync(
            self._fully_qualified_name,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnDedentAsync(self, *args, **kwargs):
        return await self._observer.OnDedentAsync(
            self._fully_qualified_name,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnStatementCompleteAsync(
        self,
        statement: Statement,
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ):
        result = await self._observer.OnStatementCompleteAsync(
            self._fully_qualified_name,
            statement,
            node,
            iter_before,
            iter_after,
        )

        if isinstance(result, Observer.ImportInfo):
            if not result.FullyQualifiedName:
                raise UnknownSourceError(
                    iter_before.Line,
                    iter_before.Column,
                    result.SourceName,
                )

            result = await self._async_parse_func(result.FullyQualifiedName)

            return False if result is None else result

        return result
