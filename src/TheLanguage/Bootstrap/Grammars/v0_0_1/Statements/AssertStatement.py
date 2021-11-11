# ----------------------------------------------------------------------
# |
# |  AssertStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-26 12:03:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the AssertStatement object"""

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

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.AssertStatementParserInfo import AssertStatementParserInfo, ExpressionParserInfo


# ----------------------------------------------------------------------
class AssertStatement(GrammarPhrase):
    """\
    A statement that asserts that a condition is true.

    'assert' <expression> (',' <expression>)?

    Examples:
        assert True
        assert a < b, "A must be smaller"
    """

    PHRASE_NAME                             = "Assert Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(AssertStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # TODO: Should use enum
                    # 'assert' | 'ensure'
                    (
                        "assert",
                        "ensure",
                    ),

                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # (',' <expression>)?
                    OptionalPhraseItem.Create(
                        name="Display Expression",
                        item=[
                            ",",
                            DynamicPhrasesType.Expressions,
                        ],
                    ),

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
            assert len(nodes) == 4

            # 'assert' | 'ensure'
            is_ensure_leaf = cast(AST.Leaf, ExtractOr(cast(AST.Node, nodes[0])))
            is_ensure_value = cast(str, ExtractToken(is_ensure_leaf))

            if is_ensure_value == "ensure":
                is_ensure_info = True
            else:
                is_ensure_leaf = None
                is_ensure_info = None

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # (',' <expression>)?
            display_expression_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
            if display_expression_node is None:
                display_expression_info = None
            else:
                display_expression_nodes = ExtractSequence(display_expression_node)
                assert len(display_expression_nodes) == 2

                display_expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, display_expression_nodes[1])))
                display_expression_info = cast(ExpressionParserInfo, GetParserInfo(display_expression_node))

            return AssertStatementParserInfo(
                CreateParserRegions(
                    node,
                    is_ensure_leaf,
                    expression_node,
                    display_expression_node,
                ),  # type: ignore
                is_ensure_info,
                expression_info,
                display_expression_info,
            )

        # ----------------------------------------------------------------------

        return Impl
