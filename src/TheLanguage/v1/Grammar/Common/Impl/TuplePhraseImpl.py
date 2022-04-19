# ----------------------------------------------------------------------
# |
# |  TuplePhraseImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 09:14:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TuplePhraseImpl object"""

import itertools
import os

from typing import cast, List

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import Tokens as CommonTokens

    from ...GrammarPhrase import AST

    from ....Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        OneOrMorePhraseItem,
        OptionalPhraseItem,
        PhraseItem,
        PhraseItemItemType,
    )

    from ....Parser.Parser import GetParserInfo, ParserInfo


# ----------------------------------------------------------------------
def Create(
    dynamic_phrases_type: DynamicPhrasesType,
) -> PhraseItemItemType:
    return (
        # Multiple Elements:
        #   '(' <dynamic_phrases_type> (',' <dynamic_phrases_type>)+ ','? ')'
        PhraseItem(
            name="Multiple Elements",
            item=[
                # '('
                "(",
                CommonTokens.PushIgnoreWhitespaceControl,

                # <dynamic_phrases_type>
                dynamic_phrases_type,

                # (',' <dynamic_phrases_type>)+
                OneOrMorePhraseItem(
                    name="Comma and Element",
                    item=[
                        ",",
                        dynamic_phrases_type,
                    ],
                ),

                # ','?
                OptionalPhraseItem(
                    name="Trailing Comma",
                    item=",",
                ),

                # ')'
                CommonTokens.PopIgnoreWhitespaceControl,
                ")",
            ],
        ),

        # Single Element:
        #   '(' <dynamic_phrases_type> ',' ')'
        PhraseItem(
            name="Single Element",
            item=[
                # '('
                "(",
                CommonTokens.PushIgnoreWhitespaceControl,

                # <dynamic_phrases_type> ','
                dynamic_phrases_type,
                ",",

                # ')'
                CommonTokens.PopIgnoreWhitespaceControl,
                ")",
            ],
        ),
    )


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> List[ParserInfo]:
    node = cast(AST.Node, ExtractOr(node))
    nodes = ExtractSequence(node)

    assert node.type is not None

    if node.type.name == "Multiple Elements":
        assert len(nodes) == 7

        enumeration_items = itertools.chain(
            [cast(AST.Node, nodes[2]), ],
            (
                cast(AST.Node, ExtractSequence(delimited_node)[1])
                for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, nodes[3])))
            ),
        )

    elif node.type.name == "Single Element":
        assert len(nodes) == 6

        enumeration_items = [cast(AST.Node, nodes[2]), ]

    else:
        assert False, node.type  # pragma: no cover

    results: List[ParserInfo] = []

    for enumeration_item in enumeration_items:
        results.append(GetParserInfo(cast(AST.Node, ExtractDynamic(enumeration_item))))

    return results
