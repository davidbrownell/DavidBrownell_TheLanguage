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
        ExtractOptional,
        ExtractOr,
        ExtractSequence,
        ExtractDynamic,
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

    <modifier>? <name> '=' <expression>

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
                    # <modifier>?
                    OptionalPhraseItem.Create(
                        item=(
                            TypeModifier.CreatePhraseItem(),
                            "once",
                        ),
                    ),

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

            # <modifier>?
            is_once_node = None
            is_once_info = None

            modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
            modifier_info = None

            if modifier_node is not None:
                modifier_node = cast(AST.Node, ExtractOr(cast(AST.Node, modifier_node)))

                if isinstance(modifier_node, AST.Leaf):
                    assert modifier_node.Type is not None
                    assert modifier_node.Type.Name == "'once'", modifier_node.Type.Name

                    is_once_node = modifier_node
                    is_once_info = True

                    modifier_node = None
                else:
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
                    is_once_node,
                ),  # type: ignore
                modifier_info,
                name_info,
                expression_info,
                is_once_info,
            )

        # ----------------------------------------------------------------------

        return Impl
