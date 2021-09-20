# ----------------------------------------------------------------------
# |
# |  TypeAliasStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-30 14:40:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeAliasStatement object"""

import os

from typing import cast, Optional

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
    from ....Parser.Statements.TypeAliasStatementParserInfo import (
        TypeAliasStatementParserInfo,
        TypeParserInfo,
    )

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
class TypeAliasStatement(GrammarPhrase):
    """\
    Create a new type name.

    'using' <name> '=' <type>

    Examples:
        using PositiveInt = Int<min_value=0>
    """

    PHRASE_NAME                             = "Type Alias Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TypeAliasStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'using'
                    "using",

                    # <name>
                    CommonTokens.TypeName,

                    # '='
                    "=",

                    # <type>
                    DynamicPhrasesType.Types,

                    CommonTokens.Newline,
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
            assert len(nodes) == 5

            # <name>
            name_leaf = cast(Leaf, nodes[1])
            name_info = cast(str, ExtractToken(name_leaf))

            # <type>
            type_node = cast(Node, ExtractDynamic(cast(Node, nodes[3])))
            type_info = cast(TypeParserInfo, GetParserInfo(type_node))

            SetParserInfo(
                node,
                TypeAliasStatementParserInfo(
                    CreateParserRegions(node, name_leaf, type_node),  # type: ignore
                    name_info,
                    type_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
