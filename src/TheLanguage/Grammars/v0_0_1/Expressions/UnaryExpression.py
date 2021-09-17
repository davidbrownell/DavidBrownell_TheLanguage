# ----------------------------------------------------------------------
# |
# |  UnaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 11:43:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryExpression object"""

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
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.Expressions.UnaryExpressionLexerInfo import (
        ExpressionLexerInfo,
        OperatorType,
        UnaryExpressionLexerInfo,
    )

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class UnaryExpression(GrammarPhrase):
    """\
    A prefix to an expression.

    <op> <expr>

    Example:
        not foo
        -bar
    """

    PHRASE_NAME                             = "Unary Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(UnaryExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <op>
                    PhraseItem(
                        name="Operator",
                        item=tuple(
                            # Note that any alphanumeric operators added here must also be added to
                            # `DoNotMatchKeywords` in ../Common/Tokens.py.
                            [
                                # Coroutine
                                "await",

                                # Transfer
                                "copy",
                                "move",

                                # Logical
                                "not",

                                # Mathematical
                                "+",
                                "-",

                                # Bit Manipulation
                                "~",        # Bit Complement
                            ],
                        ),
                    ),

                    # <expr>
                    DynamicPhrasesType.Expressions,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractLexerInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 2

            # <op>
            operator_leaf = cast(Leaf, ExtractOr(cast(Node, nodes[0])))
            op_value = cast(
                str,
                ExtractToken(
                    operator_leaf,
                    use_match=True,
                ),
            )

            if op_value == "await":
                operator_info = OperatorType.Await
            elif op_value == "copy":
                operator_info = OperatorType.Copy
            elif op_value == "move":
                operator_info = OperatorType.Move
            elif op_value == "not":
                operator_info = OperatorType.Not
            elif op_value == "+":
                operator_info = OperatorType.Positive
            elif op_value == "-":
                operator_info = OperatorType.Negative
            elif op_value == "~":
                operator_info = OperatorType.BitCompliment
            else:
                assert False, op_value

            # <expr>
            expr_node = ExtractDynamic(cast(Node, nodes[1]))
            expr_info = cast(ExpressionLexerInfo, GetLexerInfo(expr_node))

            SetLexerInfo(
                node,
                UnaryExpressionLexerInfo(
                    CreateLexerRegions(node, operator_leaf, expr_node),  # type: ignore
                    operator_info,
                    expr_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
