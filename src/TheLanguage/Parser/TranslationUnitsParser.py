# ----------------------------------------------------------------------
# |
# |  TranslationUnitsParser.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-09 23:54:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality used to parse multiple translation units simultaneously"""

import os
import threading
import traceback

from typing import Any, Awaitable, Callable, cast, Dict, List, Optional, Union

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
    from .Components.AST import Leaf, Node, RootNode    # Note that Leaf isn't used in this file but is here as a convenience
    from .Components.Error import Error
    from .Components.Normalize import Normalize
    from .Components.NormalizedIterator import NormalizedIterator
    from .Components.Phrase import Phrase

    from .TranslationUnitParser import (
        DynamicPhrasesInfo,
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
    def LoadContent(
        fully_qualified_name: str,
    ) -> str:
        """Returns the content associated with the fully qualified name"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enqueue(
        func_infos: List[Phrase.EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ExtractDynamicPhrases(
        fully_qualified_name: str,
        node: RootNode,
    ) -> DynamicPhrasesInfo:
        """Extracts phrases from the RootNode associated with the fully qualified name"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnIndentAsync(
        fully_qualified_name: str,
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Optional[DynamicPhrasesInfo]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnDedentAsync(
        fully_qualified_name: str,
        data_stack: List[Phrase.StandardParseResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    async def OnPhraseCompleteAsync(
        fully_qualified_name: str,
        phrase: Phrase,
        node: Node,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicPhrasesInfo,                 # Dynamic phases (if any) resulting from the parsed phrase
        "Observer.ImportInfo",              # Import infromation (if any) resulting from the parsed phrase
    ]:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
async def ParseAsync(
    fully_qualified_names: List[str],
    initial_phrases_info: DynamicPhrasesInfo,
    observer: Observer,
    single_threaded=False,
) -> Union[
    None,
    Dict[str, RootNode],
    List[Exception],
]:
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class SourceInfo(object):
        Node: Optional[RootNode]
        DynamicInfo: DynamicPhrasesInfo

    # ----------------------------------------------------------------------
    class ThreadInfo(object):
        # Note: not using dataclass here as it was producing too many pylint warnings

        # ----------------------------------------------------------------------
        def __init__(self):
            self.pending_ctr                = 0

            self.source_lookup: Dict[str, Optional[SourceInfo]]             = {}
            self.source_pending: Dict[str, List[threading.Event]]           = {}

            self.errors: List[Exception]    = []

    # ----------------------------------------------------------------------

    thread_info = ThreadInfo()
    thread_info_lock = threading.Lock()

    is_complete = threading.Event()

    # ----------------------------------------------------------------------
    async def ExecuteAsync(
        fully_qualified_name: str,
        increment_pending_ctr=True,
    ) -> Optional[DynamicPhrasesInfo]:

        final_result: Optional[DynamicPhrasesInfo] = None

        # ----------------------------------------------------------------------
        def OnExit():
            nonlocal final_result

            with thread_info_lock:
                source_info = thread_info.source_lookup.get(fully_qualified_name, None)
                if source_info is None:
                    del thread_info.source_lookup[fully_qualified_name]

                    final_result = DynamicPhrasesInfo([], [], [], [])
                else:
                    final_result = source_info.DynamicInfo

                for event in thread_info.source_pending.pop(fully_qualified_name, []):
                    event.set()

                if thread_info.pending_ctr == 0:
                    is_complete.set()

        # ----------------------------------------------------------------------
        class DoesNotExist(object):
            pass

        # ----------------------------------------------------------------------

        with CallOnExit(OnExit):
            with thread_info_lock:
                # Note that we can't use None to determine if the item exists within the dict, as
                # None is a valid value.
                source_info = thread_info.source_lookup.get(fully_qualified_name, DoesNotExist)

                if source_info is DoesNotExist:
                    # If here, the content needs to be parsed
                    should_execute = True
                    wait_event = None

                    thread_info.source_lookup[fully_qualified_name] = None

                    if increment_pending_ctr:
                        thread_info.pending_ctr += 1

                elif source_info is None:
                    # If here, the content is in the process of being parsed
                    should_execute = False
                    wait_event = threading.Event()

                    thread_info.source_pending.setdefault(fully_qualified_name, []).append(wait_event)

                else:
                    # If here, the content is already parsed
                    assert source_info is not DoesNotExist
                    return source_info.DynamicInfo  # type: ignore

            if should_execute:
                # ----------------------------------------------------------------------
                def OnExecuteExit():
                    with thread_info_lock:
                        assert thread_info.pending_ctr
                        thread_info.pending_ctr -= 1

                # ----------------------------------------------------------------------

                with CallOnExit(OnExecuteExit):
                    try:
                        translation_unit_observer = _TranslationUnitObserver(
                            fully_qualified_name,
                            observer,
                            ExecuteAsync,
                        )

                        content = observer.LoadContent(fully_qualified_name)

                        root = await TranslationUnitParseAsync(
                            initial_phrases_info,
                            NormalizedIterator(Normalize(content)),
                            translation_unit_observer,
                            single_threaded=single_threaded,
                        )

                        if root is None:
                            return None

                        # Get the dynamic phrases
                        dynamic_phrases = observer.ExtractDynamicPhrases(fully_qualified_name, root)

                        # Commit the results
                        with thread_info_lock:
                            assert thread_info.source_lookup[fully_qualified_name] is None
                            thread_info.source_lookup[fully_qualified_name] = SourceInfo(root, dynamic_phrases)

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
        return final_result

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
        results = await observer.Enqueue(
            [
                (ExecuteAsync, [fqn], {"increment_pending_ctr": False})
                for fqn in fully_qualified_names
            ],  #
        )

        if any(result is None for result in results):
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
        async_parse_func: Callable[[str], Awaitable[Optional[DynamicPhrasesInfo]]],
    ):
        self._fully_qualified_name          = fully_qualified_name
        self._observer                      = observer
        self._async_parse_func              = async_parse_func

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        func_infos: List[Phrase.EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        return self._observer.Enqueue(func_infos)

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
    async def OnPhraseCompleteAsync(
        self,
        phrase: Phrase,
        node: Node,
        iter_before: NormalizedIterator,
        iter_after: NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicPhrasesInfo,                 # Dynamic phases (if any) resulting from the parsed phrase
    ]:
        result = await self._observer.OnPhraseCompleteAsync(
            self._fully_qualified_name,
            phrase,
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

            return await self._async_parse_func(result.FullyQualifiedName) or False

        return result
