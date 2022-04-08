# ----------------------------------------------------------------------
# |
# |  Lexer.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 11:17:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that Lexes content"""

import os

from typing import Any, Awaitable, Dict, List, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Components.ThreadPool import CreateThreadPool, ThreadPoolExecutor

    from .TranslationUnitsLexer import (
        AST,
        DynamicPhrasesInfo,
        EnqueueAsyncItemType,
        Observer as TranslationUnitsObserver,
        Lex as TranslationUnitsLex,
        Phrase,
        RegexToken,
    )


# ----------------------------------------------------------------------
class Observer(Interface.Interface):
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
    def OnPhraseComplete(
        fully_qualified_name: str,
        phrase: Phrase,
        iter_range: Phrase.NormalizedIteratorRange,
        node: AST.Node,
    ) -> Union[
        bool,                               # True to continue, False to terminate
        DynamicPhrasesInfo,                 # Dynamic phrases to add to the active scope as a result of completing this phrase
        TranslationUnitsObserver.ImportInfo # Import information (if any) resulting from the completion of the parsed phrase
    ]:
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
def Lex(
    comment_token: RegexToken,
    grammar: DynamicPhrasesInfo,
    fully_qualified_names: List[str],
    observer: Observer,
    *,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,                                   # Cancelled
    Dict[str, AST.Node],                    # Successful results
    List[Exception],                        # Errors
]:
    """\
    Returns AST(s) for the given names (where each name represents content).

    The results of this function can be used to completely regenerate the original source (which can
    be valuable for creating things like source formatting tools). However, this data set contains
    extraneous data that can make parsing more difficult (for example, ignored tokens like comments
    and whitespace will remain in the lexed AST).

    The 'Prune' function should be used on successful output of this function before any further
    parsing is invoked.
    """

    translation_units_observer = _TranslationUnitsObserver(observer, max_num_threads)

    return TranslationUnitsLex(
        comment_token,
        fully_qualified_names,
        grammar,
        translation_units_observer,
        single_threaded=max_num_threads == 1,
    )


# ----------------------------------------------------------------------
def Prune(
    roots: Dict[str, AST.Node],
    *,
    max_num_threads: Optional[int]=None,
) -> None:
    """Removes notes that have been explicitly ignored (for easier parsing)"""

    single_threaded = max_num_threads == 1 or len(roots) == 1

    if single_threaded:
        for v in roots.values():
            _Prune(v)
    else:
        with ThreadPoolExecutor(
            max_workers=max_num_threads,
        ) as executor:
            futures = [
                executor.submit(lambda v=v: _Prune(v))
                for v in roots.values()
            ]

            [future.result() for future in futures]


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _TranslationUnitsObserver(TranslationUnitsObserver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        observer: Observer,
        max_num_threads: Optional[int]=None,
    ):
        assert max_num_threads is None or max_num_threads > 0, max_num_threads

        self._observer                      = observer
        self._executor                      = CreateThreadPool(max_workers=max_num_threads)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def LoadContent(
        fully_qualified_name: str,
    ) -> str:
        assert os.path.isfile(fully_qualified_name), fully_qualified_name

        with open(fully_qualified_name) as f:
            content = f.read()

        return content

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractDynamicPhrases(
        self,
        fully_qualified_name: str,
        node: AST.Node,
    ) -> DynamicPhrasesInfo:
        # TODO

        # pylint: disable=too-many-function-args
        return DynamicPhrasesInfo({})

    # ----------------------------------------------------------------------
    @Interface.override
    def GetParentStatementNode(
        self,
        node: AST.Node,
    ) -> Optional[AST.Node]:
        return self._observer.GetParentStatementNode(node)

    # ----------------------------------------------------------------------
    @Interface.override
    def Enqueue(
        self,
        func_infos: List[EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        raise Exception("Async functionality has been partially removed and simply doesn't work right now")
        # return self._executor.EnqueueAsync(func_infos)  # type: ignore  # pylint: disable=not-callable

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def OnPushScope(
        fully_qualified_name: str,
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> Optional[DynamicPhrasesInfo]:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def OnPopScope(
        fully_qualified_name: str,
        iter_range: Phrase.NormalizedIteratorRange,
        data: Phrase.LexResultData,
    ) -> None:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    def OnPhraseComplete(
        self,
        fully_qualified_name: str,
        phrase: Phrase,
        iter_range: Phrase.NormalizedIteratorRange,
        node: AST.Node,
    ) -> Union[
        bool,                                           # True to continue, False to terminate
        DynamicPhrasesInfo,                             # Dynamic phrases to add to the active scope
        TranslationUnitsObserver.ImportInfo,            # Import information (if any) resulting from the parsed phrase
    ]:
        return self._observer.OnPhraseComplete(fully_qualified_name, phrase, iter_range, node)


# ----------------------------------------------------------------------
def _Prune(
    node: AST.Node,
) -> None:
    child_index = 0

    while child_index < len(node.children):
        child = node.children[child_index]

        should_delete = False

        if isinstance(child, AST.Leaf) and child.is_ignored:
            should_delete = True
        elif isinstance(child, AST.Node):
            _Prune(child)

            if not child.children:
                should_delete = True

        if not should_delete:
            child_index += 1
            continue

        del node.children[child_index]
