# ----------------------------------------------------------------------
# |
# |  AllGrammars.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 12:04:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Loads all the grammars"""

import os

from typing import Dict, List, Optional, Set, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Grammar.All import GrammarPhrases

    from .Grammar.GrammarPhrase import (
        CommentToken,
        DynamicPhrasesType,
        GetParentStatementNode as GetParentStatementNodeImpl,
        GrammarPhrase,
        ImportGrammarPhrase,
        RegexToken,
    )

    from .Lexer.Lexer import (
        AST,
        DynamicPhrasesInfo,
        Observer as LexObserverBase,
        Phrase as LexerPhrase,
        TranslationUnitsObserver,
    )

    from .Parser.Parser import ParseObserver as ParseObserverBase


# ----------------------------------------------------------------------
def _LoadGrammars() -> Tuple[
    DynamicPhrasesInfo,
    RegexToken,
    Dict[LexerPhrase, GrammarPhrase],
]:
    name_lookup: Set[str] = set()
    dynamic_phrases: Dict[DynamicPhrasesType, List[LexerPhrase]] = {}
    phrase_lookop: Dict[LexerPhrase, GrammarPhrase] = {}

    for grammar_phrase in GrammarPhrases:
        assert grammar_phrase.phrase.name not in name_lookup, grammar_phrase.phrase.name
        name_lookup.add(grammar_phrase.phrase.name)

        dynamic_phrases.setdefault(grammar_phrase.type, []).append(grammar_phrase.phrase)

        assert grammar_phrase.phrase not in phrase_lookop, grammar_phrase.phrase
        phrase_lookop[grammar_phrase.phrase] = grammar_phrase

    return (
        DynamicPhrasesInfo.Create(
            dynamic_phrases,
            allow_parent_traversal=False,
            name="Default Grammar",
        ),
        CommentToken,
        phrase_lookop,
    )


(
    Grammar,
    GrammarCommentToken,
    GrammarPhraseLookup,
) = _LoadGrammars()


# ----------------------------------------------------------------------
class LexObserver(LexObserverBase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        source_roots: List[str],
    ):
        for source_root in source_roots:
            assert os.path.isdir(source_root), source_root

        self._source_roots                  = source_roots

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetParentStatementNode(
        node: AST.Node,
    ) -> Optional[AST.Node]:
        return GetParentStatementNodeImpl(node)

    # ----------------------------------------------------------------------
    @Interface.override
    def OnPhraseComplete(
        self,
        fully_qualified_name: str,
        phrase: LexerPhrase,
        iter_range: LexerPhrase.NormalizedIteratorRange,
        node: AST.Node,
    ) -> Union[
        bool,
        DynamicPhrasesInfo,
        TranslationUnitsObserver.ImportInfo,
    ]:
        try:
            grammar_phrase = GrammarPhraseLookup.get(phrase, None)
        except TypeError:
            grammar_phrase = None

        if grammar_phrase is not None:
            if isinstance(grammar_phrase, ImportGrammarPhrase):
                return grammar_phrase.ProcessImportNode(
                    self._source_roots,
                    fully_qualified_name,
                    node,
                )

            result = grammar_phrase.GetDynamicContent(node)

            # TODO: Process result in case the syntax is changing

        return True


# ----------------------------------------------------------------------
class ParseObserver(ParseObserverBase):
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> ParseObserverBase.ExtractParserInfoReturnType:
        if isinstance(node.type, LexerPhrase):
            grammar_phrase = GrammarPhraseLookup.get(node.type, None)
            if grammar_phrase is not None:
                return grammar_phrase.ExtractParserInfo(node)

        return None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractPotentialDocInfo(
        node: Union[AST.Leaf, AST.Node],
    ) -> Optional[Tuple[AST.Leaf, str]]:
        return None # TODO
        # TODO: if isinstance(node.type, LexerPhrase):
        # TODO:     if isinstance(node.type, DynamicPhrase):
        # TODO:         node = ExtractDynamic(node)
