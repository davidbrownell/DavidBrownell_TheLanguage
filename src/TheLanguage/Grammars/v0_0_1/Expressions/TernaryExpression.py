# ----------------------------------------------------------------------
# |
# |  TernaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 16:47:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpression object"""

import os

from typing import Callable, cast, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractSequence,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Expressions.TernaryExpressionParserInfo import (
        ExpressionParserInfo,
        TernaryExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class TernaryExpression(GrammarPhrase):
    """\
    Experssion that returns one value when a condition is True and a different one when it is false.

    <expression> 'if' <expression> 'else' <expression>

    Examples:
        "The Truth" if SomeExpr() else "The Lie"
    """

    PHRASE_NAME                             = "Ternary Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TernaryExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expression> (true)
                    DynamicPhrasesType.Expressions,

                    # 'if'
                    "if",

                    # <expression> (condition)
                    DynamicPhrasesType.Expressions,

                    # 'else'
                    "else",

                    # <expression> (false)
                    DynamicPhrasesType.Expressions,
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
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            # <expression> (true)
            true_node = ExtractDynamic(cast(AST.Node, nodes[0]))
            true_info = cast(ExpressionParserInfo, GetParserInfo(true_node))

            # <expression> (condition)
            condition_node = ExtractDynamic(cast(AST.Node, nodes[2]))
            condition_info = cast(ExpressionParserInfo, GetParserInfo(condition_node))

            # <expression> (false)
            false_node = ExtractDynamic(cast(AST.Node, nodes[4]))
            false_info = cast(ExpressionParserInfo, GetParserInfo(false_node))

            return TernaryExpressionParserInfo(
                CreateParserRegions(node, condition_node, true_node, false_node),  # type: ignore
                condition_info,
                true_info,
                false_info,
            )

        # ----------------------------------------------------------------------

        return Impl
