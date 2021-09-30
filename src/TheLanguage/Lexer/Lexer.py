# ----------------------------------------------------------------------
# |
# |  Lexer.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-27 22:46:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that Lexes content"""

import asyncio
import os

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Components.ThreadPool import CreateThreadPool

    from .SyntaxObserverDecorator import (
        Configurations,
        SemVer,
        SyntaxObserverDecorator,
    )

    from .TranslationUnitsLexer import (
        AST,
        DynamicPhrasesInfo,
        Observer as TranslationUnitsObserver,
        LexAsync as TranslationUnitsLexAsync,
        Phrase,
        RegexToken,
    )


# ----------------------------------------------------------------------
OnPhraseCompleteFuncType                    = Callable[
    [
        str,                                            # fully_qualified_name
        Phrase,                                         # phrase
        AST.Node,                                       # node
        Phrase.NormalizedIterator,                      # iter_before
        Phrase.NormalizedIterator,                      # iter_after
    ],
    Union[
        bool,                                           # True to continue processing, False to terminate
        DynamicPhrasesInfo,                             # Dynamic phrases (if any) resulting from the completion of the parsed phrase
        TranslationUnitsObserver.ImportInfo,            # Import information (if any) resulting from the completion of the parsed phrase
    ]
]


# ----------------------------------------------------------------------
def Lex(
    comment_token: RegexToken,
    grammars: Dict[SemVer, DynamicPhrasesInfo],
    configuration: Configurations,
    target: str,
    fully_qualified_names: List[str],
    source_roots: List[str],
    on_phrase_complete_func: OnPhraseCompleteFuncType,
    *,
    default_grammar: Optional[SemVer]=None,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,                                   # Cancellation
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

    observer = SyntaxObserverDecorator(
        _TranslationUnitsObserver(
            source_roots,
            on_phrase_complete_func,
            max_num_threads,
        ),
        grammars,
        configuration,
        target,
        default_grammar,
    )

    return asyncio.get_event_loop().run_until_complete(
        TranslationUnitsLexAsync(
            comment_token,
            fully_qualified_names,
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
            single_threaded=max_num_threads==1,
        ),
    )


# ----------------------------------------------------------------------
def Prune(
    roots: Dict[str, AST.Node],
    *,
    max_num_threads: Optional[int]=None,
):
    """Removes nodes that have been explicitly ignored (for easier parsing)"""

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
        source_roots: List[str],
        on_phrase_complete_func: OnPhraseCompleteFuncType,
        max_num_threads: Optional[int]=None,
    ):
        for source_root in source_roots:
            assert os.path.isdir(source_root), source_root

        assert on_phrase_complete_func
        assert max_num_threads is None or max_num_threads > 0, max_num_threads

        self._source_roots                  = source_roots
        self._on_phrase_complete_func       = on_phrase_complete_func
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
    def Enqueue(
        self,
        func_infos: List[Phrase.EnqueueAsyncItemType],
    ) -> Awaitable[Any]:
        # pylint: disable=not-callable
        return self._executor.EnqueueAsync(func_infos)  # type: ignore

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
    @staticmethod
    @Interface.override
    async def OnPushScopeAsync(
        fully_qualified_name: str,
        data: Phrase.StandardLexResultData,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Optional[DynamicPhrasesInfo]:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    async def OnPopScopeAsync(
        fully_qualified_name: str,
        data: Phrase.StandardLexResultData,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> None:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    async def OnPhraseCompleteAsync(
        self,
        fully_qualified_name: str,
        phrase: Phrase,
        node: AST.Node,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Union[
        bool,                               # True to continue processing, False to terminate
        DynamicPhrasesInfo,                 # Dynamic phrases to add to the active scope as a result of completing this phrase
        TranslationUnitsObserver.ImportInfo,# Import information (if any) resulting from the parsed phrase
    ]:
        return self._on_phrase_complete_func(
            fully_qualified_name,
            phrase,
            node,
            iter_before,
            iter_after,
        )


# ----------------------------------------------------------------------
def _Prune(
    node: AST.Node,
):
    child_index = 0

    while child_index < len(node.Children):
        child = node.Children[child_index]

        should_delete = False

        if child.IsIgnored:
            should_delete = True

        elif isinstance(child, AST.Node):
            _Prune(child)

            if not child.Children:
                should_delete = True

        if not should_delete:
            child_index += 1
            continue

        del node.Children[child_index]
