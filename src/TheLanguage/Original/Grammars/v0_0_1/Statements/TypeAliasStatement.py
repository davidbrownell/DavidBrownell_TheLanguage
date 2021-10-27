# ----------------------------------------------------------------------
# |
# |  TypeAliasStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 13:22:30
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

from typing import Callable, cast, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractSequence,
        ExtractToken,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.TypeAliasStatementParserInfo import (
        TypeAliasStatementParserInfo,
        TypeParserInfo,
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
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'using'
                    "using",

                    # <generic_name>
                    CommonTokens.GenericUpperName,

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
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            # <generic_name>
            name_leaf = cast(AST.Leaf, nodes[1])
            name_info = cast(str, ExtractToken(name_leaf))

            if not CommonTokens.TypeNameRegex.match(name_info):
                raise CommonTokens.InvalidTokenError(name_leaf, name_info, "type")

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[3])))
            type_info = cast(TypeParserInfo, GetParserInfo(type_node))

            return TypeAliasStatementParserInfo(
                CreateParserRegions(node, name_leaf, type_node),  # type: ignore
                name_info,
                type_info,
            )

        # ----------------------------------------------------------------------

        return Impl
