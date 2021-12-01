# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 13:29:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableDeclarationStatement object"""

import os

from typing import Callable, cast, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Common import TypeModifier

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.VariableDeclarationStatementParserInfo import (
        ExpressionParserInfo,
        NameParserInfo,
        VariableDeclarationStatementParserInfo,
    )


# ----------------------------------------------------------------------
class VariableDeclarationStatement(GrammarPhrase):
    """\
    Declares a variable.

    <modifier> <name> '=' <expression>

    Examples:
        foo = bar
        (a, b,) = Func()
    """

    PHRSE_NAME                              = "Variable Declaration Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableDeclarationStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRSE_NAME,
                item=[
                    # <modifier>
                    TypeModifier.CreatePhraseItem(),

                    # <name>
                    DynamicPhrasesType.Names,

                    "=",

                    # <expression>
                    DynamicPhrasesType.Expressions,
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

            # <modifier>
            modifier_node = cast(AST.Node, nodes[0])
            modifier_info = TypeModifier.Extract(modifier_node)

            # <name>
            name_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
            name_info = cast(NameParserInfo, GetParserInfo(name_node))

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[3])))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return VariableDeclarationStatementParserInfo(
                CreateParserRegions(
                    node,
                    modifier_node,
                    name_node,
                    expression_node,
                ),  # type: ignore
                modifier_info,
                name_info,
                expression_info,
            )

        # ----------------------------------------------------------------------

        return Impl
