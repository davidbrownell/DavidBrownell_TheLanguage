# ----------------------------------------------------------------------
# |
# |  Lex.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 14:22:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that lexes content"""

import asyncio
import os

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Dict, List, Optional, Union

from semantic_version import Version as SemVer

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Components.ThreadPool import CreateThreadPool

    # TODO: Consider adding if functionality for targets and configuration similar to the Syntax decorator
    from .Syntax import Observer as SyntaxObserver

    from .TranslationUnitsLexer import (
        DynamicPhrasesInfo,
        Leaf,
        Node,
        Observer as TranslationUnitsObserver,
        LexAsync as TranslationUnitsLexAsync,
        Phrase,
        RootNode,
    )

    from ..Grammars.GrammarPhrase import GrammarPhrase, ImportGrammarStatement


# ----------------------------------------------------------------------
def Lex(
    grammars: Dict[SemVer, DynamicPhrasesInfo],
    grammar_phrase_lookup: Dict[Phrase, GrammarPhrase],
    fully_qualified_names: List[str],
    source_roots: List[str],
    *,
    max_num_threads: Optional[int]=None,
) -> Union[
    None,                                   # Cancellation
    Dict[str, RootNode],                    # Successful results
    List[Exception],                        # Errors
]:
    """\
    Return AST(s) for the given names.

    This information can be used to complete regenerate the original source (which can be valuable for
    writing things like source formatting tools). However, it contains extraneous data that can make
    parsing more difficult (for example, ignored tokens that comments and whitespace remain in the AST).

    The 'Prune' function should be used on the successful result of this function before further
    processing is invoked.
    """

    syntax_observer = SyntaxObserver(
        _LexObserver(
            grammar_phrase_lookup,
            source_roots,
            max_num_threads=max_num_threads,
        ),
        grammars,
    )

    return asyncio.get_event_loop().run_until_complete(
        TranslationUnitsLexAsync(
            fully_qualified_names,
            syntax_observer.Syntaxes[syntax_observer.DefaultVersion],
            syntax_observer,
            single_threaded=max_num_threads == 1,
        ),
    )


# ----------------------------------------------------------------------
def Prune(
    roots: Dict[str, RootNode],
    *,
    max_num_threads: Optional[int]=None,
):
    """Removes Leaf nodes that have been explicitly ignored (for easier parsing)"""

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
class _LexObserver(TranslationUnitsObserver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        grammar_phrase_lookup: Dict[Phrase, GrammarPhrase],
        source_roots: List[str],
        max_num_threads: Optional[int]=None,
    ):
        for source_root in source_roots:
            assert os.path.isdir(source_root), source_root

        assert max_num_threads is None or max_num_threads > 0, max_num_threads

        self._is_cancelled                  = False
        self._grammar_phrase_lookup         = grammar_phrase_lookup
        self._source_roots                  = source_roots
        self._executor                      = CreateThreadPool(max_workers=max_num_threads)

    # ----------------------------------------------------------------------
    def Cancel(self):
        self._is_cancelled = True

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
        node: RootNode,
    ) -> DynamicPhrasesInfo:
        # TODO

        # pylint: disable=too-many-function-args
        return DynamicPhrasesInfo([], [], [], [])

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    async def OnIndentAsync(
        fully_qualified_name: str,
        data_stack: List[Phrase.StandardLexResultData],
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Optional[DynamicPhrasesInfo]:
        # Nothing to do here
        return None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    async def OnDedentAsync(
        fully_qualified_name: str,
        data_stack: List[Phrase.StandardLexResultData],
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
        node: Node,
        iter_before: Phrase.NormalizedIterator,
        iter_after: Phrase.NormalizedIterator,
    ) -> Union[
        bool,                                           # True to continue processing, False to terminate
        DynamicPhrasesInfo,                             # Dynamic phases (if any) resulting from the parsed phrase
        TranslationUnitsObserver.ImportInfo,            # Import information (if any) resulting from the parsed phrase
    ]:
        try:
            grammar_phrase = self._grammar_phrase_lookup.get(phrase, None)
        except TypeError:
            grammar_phrase = None

        if grammar_phrase is not None:
            if isinstance(grammar_phrase, ImportGrammarStatement):
                return grammar_phrase.ProcessImportStatement(
                    self._source_roots,
                    fully_qualified_name,
                    node,
                )

        return not self._is_cancelled


# ----------------------------------------------------------------------
def _Prune(
    node: Union[RootNode, Node],
):
    child_index = 0

    while child_index < len(node.Children):
        child = node.Children[child_index]

        should_delete = False

        if isinstance(child, Node):
            _Prune(child)

            if not child.Children:
                should_delete = True

        elif isinstance(child, Leaf):
            if child.IsIgnored:
                should_delete = True

        else:
            assert False, child  # pragma: no cover

        if not should_delete:
            child_index += 1
            continue

        del node.Children[child_index]
