# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 14:34:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

import os

from typing import cast, Dict, List, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import GrammarPhrase

    from ....Lexer.ParserInterfaces.Types.VariantTypeLexerInfo import LexerInfo, VariantTypeLexerInfo

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractRepeat,
        ExtractSequence,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class VariantType(GrammarPhrase):
    """\
    A type that can be any one of a collection of types.

    '(' <type> '|' (<type> '|')* <type> ')'

    Examples:
        (Int | Float)
        (Int val | Bool | Char view)
    """

    PHRASE_NAME                             = "Variant Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariantType, self).__init__(
            GrammarPhrase.Type.Type,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <type>
                    DynamicPhrasesType.Types,

                    # '|'
                    "|",

                    # (<type> '|')*
                    PhraseItem(
                        name="Type and Sep",
                        item=[
                            DynamicPhrasesType.Types,
                            "|",
                        ],
                        arity="*",
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # ")"
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ValidateSyntax(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            token_lookup: Dict[str, Union[Leaf, Node]] = {
                "self": node,
            }

            nodes = ExtractSequence(node)
            assert len(nodes) == 8

            types: List[LexerInfo] = []

            # <type>
            types.append(ExtractDynamic(cast(Node, nodes[2])).Info)  # type: ignore

            # (<type> '|') *
            for child in cast(List[Node], ExtractRepeat(cast(Node, nodes[4]))):
                child_nodes = ExtractSequence(child)
                assert len(child_nodes) == 2

                types.append(ExtractDynamic(cast(Node, child_nodes[0])).Info)  # type: ignore

            # <type>
            types.append(ExtractDynamic(cast(Node, nodes[5])).Info)  # type: ignore

            # Save the data
            object.__setattr__(
                node,
                "Info",
                # pylint: disable=too-many-function-args
                VariantTypeLexerInfo(
                    token_lookup,
                    types,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ValidateSyntaxResult(CreateLexerInfo)
