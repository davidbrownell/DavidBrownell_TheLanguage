# ----------------------------------------------------------------------
# |
# |  VariantPhraseImpl.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 09:39:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantPhraseImpl object"""

import itertools
import os

from typing import cast, List, Optional

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
        ExtractRepeat,
        ExtractSequence,
        PhraseItemItemType,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import GetPhrase, Phrase as ParserPhrase


# ----------------------------------------------------------------------
def Create(
    dynamic_phrases_type: DynamicPhrasesType,
) -> PhraseItemItemType:
    return [
        # '('
        "(",
        CommonTokens.PushIgnoreWhitespaceControl,

        # <dynamic_phrases_type> '|'
        dynamic_phrases_type,
        "|",

        # ( <dynamic_phrases_type> '|' )*
        ZeroOrMorePhraseItem(
            name="Element and Separator",
            item=[
                dynamic_phrases_type,
                "|",
            ],
        ),

        # <dynamic_phrases_type>
        dynamic_phrases_type,

        # ')'
        CommonTokens.PopIgnoreWhitespaceControl,
        ")",
    ]


# ----------------------------------------------------------------------
def Extract(
    node: AST.Node,
) -> List[ParserPhrase]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 8

    results: List[ParserPhrase] = []

    for enumeration_item in  itertools.chain(
        [cast(AST.Node, nodes[2]), ],
        (
            cast(AST.Node, ExtractSequence(delimited_node)[0])
            for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(Optional[AST.Node], nodes[4])))
        ),
        [cast(AST.Node, nodes[5]), ],
    ):
        results.append(GetPhrase(cast(AST.Node, ExtractDynamic(enumeration_item))))

    return results
