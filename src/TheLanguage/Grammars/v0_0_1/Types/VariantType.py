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

from typing import cast, List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import CreateParserRegions, GrammarPhrase

    from ....Parser.ParserInfo import GetParserInfo, SetParserInfo
    from ....Parser.Types.VariantTypeParserInfo import (
        TypeParserInfo,
        VariantTypeParserInfo,
    )

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractRepeat,
        ExtractSequence,
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
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        # ----------------------------------------------------------------------
        def CreateParserInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 8

            type_infos: List[TypeParserInfo] = []

            # <type>
            type_infos.append(cast(TypeParserInfo, GetParserInfo(ExtractDynamic(cast(Node, nodes[2])))))

            # (<type> '|') *
            for child in cast(List[Node], ExtractRepeat(cast(Node, nodes[4]))):
                child_nodes = ExtractSequence(child)
                assert len(child_nodes) == 2

                type_infos.append(cast(TypeParserInfo, GetParserInfo(ExtractDynamic(cast(Node, child_nodes[0])))))

            # <type>
            type_infos.append(cast(TypeParserInfo, GetParserInfo(ExtractDynamic(cast(Node, nodes[5])))))

            # pylint: disable=too-many-function-args
            SetParserInfo(
                node,
                VariantTypeParserInfo(
                    CreateParserRegions(node, node),  # type: ignore
                    type_infos,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
