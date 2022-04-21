# ----------------------------------------------------------------------
# |
# |  TranslationUnitsLexer.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 13:52:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality used to lex multiple translation units simultaneously"""

import os
import threading
import traceback

from typing import Callable, cast, Dict, List, Optional, Union

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
    from .Error import CreateError

    from .Components.Normalize import Normalize

    from .TranslationUnitLexer import (
        AST,
        DynamicPhrasesInfo,
        EnqueueFuncInfoType,
        EnqueueReturnType,
        Lex as TranslationUnitLex,
        Observer as TranslationUnitObserver,
        NormalizedIterator,
        Phrase,
        RegexToken,
    )


# ----------------------------------------------------------------------
UnknownSourceError                          = CreateError(
    "'{source_name}' could not be found",
    source_name=str,
)


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ImportInfo(object):
        source_name: str
        fully_qualified_name: Optional[str] # None if the source name cannot be resolved

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
    def ExtractDynamicPhrases(
        fully_qualified_name: str,
        node: AST.Node,
    ) -> DynamicPhrasesInfo:
        """Extracts phrases from the Node associated with the fully qualified name"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def GetParentStatementNode(
        node: AST.Node,
    ) -> Optional[AST.Node]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Enqueue(
        func_infos: List[EnqueueFuncInfoType],
    ) -> EnqueueReturnType:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnPushScope(
        fully_qualified_name: str,
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> Optional[DynamicPhrasesInfo]:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnPopScope(
        fully_qualified_name: str,
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> None:
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def OnPhraseComplete(
        fully_qualified_name: str,
        phrase: Phrase,
        iter_range: Phrase.NormalizedIteratorRange,
        node: AST.Node,
    ) -> Union[
        bool,                               # True to continue, False to terminate
        DynamicPhrasesInfo,                 # Dynamic phrases to add to the active scope
        "Observer.ImportInfo",              # Import information (if any) resulting from the parsed phrase
    ]:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
def Lex(
    comment_token: RegexToken,
    fully_qualified_names: List[str],
    initial_phrases_info: DynamicPhrasesInfo,
    observer: Observer,
    single_threaded=False,
) -> Union[
    None,
    Dict[str, AST.Node],
    List[Exception],
]:
    if len(fully_qualified_names) == 1:
        single_threaded = True

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class SourceInfo(object):
        node: Optional[AST.Node]
        dynamic_info: DynamicPhrasesInfo

    # ----------------------------------------------------------------------
    class ThreadInfo(object):
        # ----------------------------------------------------------------------
        def __init__(self):
            self.pending_ctr                = 0

            self.source_lookup: Dict[str, Optional[SourceInfo]]             = {}
            self.source_pending: Dict[str, List[threading.Event]]           = {}

            self.errors: List[Exception]                                    = []

    # ----------------------------------------------------------------------

    thread_info = ThreadInfo()
    thread_info_lock = threading.Lock()

    is_complete = threading.Event()

    # ----------------------------------------------------------------------
    def Execute(
        fully_qualified_name: str,
        increment_pending_ctr=True,
    ) -> Optional[DynamicPhrasesInfo]:
        final_result: Optional[DynamicPhrasesInfo] = None

        # ----------------------------------------------------------------------
        class DoesNotExist(object):
            pass

        # ----------------------------------------------------------------------
        def OnExit():
            nonlocal final_result

            with thread_info_lock:
                source_info = thread_info.source_lookup.get(fully_qualified_name, DoesNotExist)

                if source_info is DoesNotExist:
                    final_result = DynamicPhrasesInfo.Create({})

                elif source_info is None:
                    del thread_info.source_lookup[fully_qualified_name]

                    final_result = DynamicPhrasesInfo.Create({})
                else:
                    assert isinstance(source_info, SourceInfo), source_info
                    final_result = source_info.dynamic_info

                for event in thread_info.source_pending.pop(fully_qualified_name, []):
                    event.set()

                if thread_info.pending_ctr == 0:
                    is_complete.set()

        # ----------------------------------------------------------------------

        with CallOnExit(OnExit):
            with thread_info_lock:
                # Note that we can't use None to determine if the item exists within the dict as
                # None is a valid value.
                source_info = thread_info.source_lookup.get(fully_qualified_name, DoesNotExist)

                if source_info is DoesNotExist:
                    # If here, the content needs to be lexed
                    should_execute = True
                    wait_event = None

                    thread_info.source_lookup[fully_qualified_name] = None

                    if increment_pending_ctr:
                        thread_info.pending_ctr += 1

                elif source_info is None:
                    # If here, the content is already being lexed
                    should_execute = False
                    wait_event = threading.Event()

                    thread_info.source_pending.setdefault(fully_qualified_name, []).append(wait_event)

                else:
                    # If here, the content has already been lexed
                    assert source_info is not DoesNotExist
                    return source_info.dynamic_info  # type: ignore

            if should_execute:
                # ----------------------------------------------------------------------
                def OnExecuteExit():
                    with thread_info_lock:
                        assert thread_info.pending_ctr
                        thread_info.pending_ctr -= 1

                # ----------------------------------------------------------------------

                with CallOnExit(OnExecuteExit):
                    try:
                        content = observer.LoadContent(fully_qualified_name)

                        # ----------------------------------------------------------------------
                        def SuppressIndentationInfo(
                            offset_start: int,          # type: ignore  # pylint: disable=unused-argument
                            offset_end: int,            # type: ignore  # pylint: disable=unused-argument
                            content_start: int,
                            content_end: int,
                        ) -> bool:
                            return bool(
                                comment_token.regex.match(
                                    content,
                                    pos=content_start,
                                    endpos=content_end,
                                ),
                            )

                        # ----------------------------------------------------------------------

                        normalized_iter = NormalizedIterator.FromNormalizedContent(
                            Normalize(
                                content,
                                suppress_indentation_func=SuppressIndentationInfo,
                            ),
                        )

                        translation_unit_observer = _TranslationUnitObserver(
                            fully_qualified_name,
                            observer,
                            Execute,
                        )

                        root = TranslationUnitLex(
                            comment_token,
                            initial_phrases_info,
                            normalized_iter,
                            translation_unit_observer,
                            single_threaded=single_threaded,
                        )

                        if root is None:
                            return None

                        dynamic_phrases = observer.ExtractDynamicPhrases(fully_qualified_name, root)

                        # Commit the results
                        with thread_info_lock:
                            assert thread_info.source_lookup[fully_qualified_name] is None
                            thread_info.source_lookup[fully_qualified_name] = SourceInfo(root, dynamic_phrases)

                    except Exception as ex:  # pylint: disable=broad-except
                        assert not hasattr(ex, "traceback")
                        object.__setattr__(ex, "traceback", traceback.format_exc())

                        assert not hasattr(ex, "fully_qualified_name")
                        object.__setattr__(ex, "fully_qualified_name", fully_qualified_name)

                        with thread_info_lock:
                            thread_info.errors.append(ex)

            elif wait_event is not None:
                wait_event.wait()

        assert final_result is not None
        return final_result

    # ----------------------------------------------------------------------

    with thread_info_lock:
        # Prepopulate `pending_ctr` so that we can make sure that we don't
        # prematurely terminate as threads are spinning up.
        thread_info.pending_ctr = len(fully_qualified_names)

    if single_threaded:
        for fqn in fully_qualified_names:
            result = Execute(fqn, increment_pending_ctr=False)
            if result is None:
                return None
    else:
        results = observer.Enqueue(
            [
                (Execute, [fqn], {"increment_pending_ctr": False})
                for fqn in fully_qualified_names
            ],
        )

        if any(result is None for result in results):
            return None

        is_complete.wait()

    assert not thread_info.source_pending, thread_info.source_pending

    if thread_info.errors:
        return thread_info.errors

    return {
        fqn: cast(AST.Node, cast(SourceInfo, source_info).node)
        for fqn, source_info in thread_info.source_lookup.items()
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
        lex_func: Callable[[str], Optional[DynamicPhrasesInfo]],
    ):
        self._fully_qualified_name          = fully_qualified_name
        self._observer                      = observer
        self._lex_func                      = lex_func
        self._prev_line                     = None

    # ----------------------------------------------------------------------
    @Interface.override
    def GetParentStatementNode(self, *args, **kwargs):
        return self._observer.GetParentStatementNode(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(self, *args, **kwargs):
        return self._observer.Enqueue(*args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnPushScope(self, *args, **kwargs):
        return self._observer.OnPushScope(self._fully_qualified_name, *args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnPopScope(self, *args, **kwargs):
        return self._observer.OnPopScope(self._fully_qualified_name, *args, **kwargs)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnPhraseComplete(
        self,
        phrase: Phrase,
        iter_range: Phrase.NormalizedIteratorRange,
        node: AST.Node,
    ) -> Union[
        bool,
        DynamicPhrasesInfo,
    ]:
        if self._prev_line is None or iter_range.end.line > self._prev_line:
            self._prev_line = iter_range.end.line

            self._prev_line = iter_range.end.line
            print(
                "[Temp Diagnostic] Parsed [Ln {} -> Ln {}] {}".format(
                    iter_range.begin.line,
                    iter_range.end.line,
                    self._fully_qualified_name,
                ),
            )

        result = self._observer.OnPhraseComplete(
            self._fully_qualified_name,
            phrase,
            iter_range,
            node,
        )

        if isinstance(result, Observer.ImportInfo):
            if not result.fully_qualified_name:
                raise UnknownSourceError.Create(
                    location=iter_range.begin.ToLocation(),
                    source_name=result.source_name,
                )

            result = self._lex_func(result.fully_qualified_name)
            if result is None:
                return False

        return result
