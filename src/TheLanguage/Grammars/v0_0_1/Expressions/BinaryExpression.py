# ----------------------------------------------------------------------
# |
# |  BinaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 15:42:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryExpression object"""

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

    from ....Lexer.Expressions.BinaryExpressionLexerInfo import (
        BinaryExpressionLexerData,
        BinaryExpressionLexerInfo,
        BinaryExpressionLexerRegions,
        ExpressionLexerInfo,
        OperatorType,
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
    )


# ----------------------------------------------------------------------
class BinaryExpression(GrammarPhrase):
    """\
    Expression that follows the form:

    <expr> <op> <expr>

    Example:
        one + two
        foo / bar
        biz and baz
    """

    PHRASE_NAME                             = "Binary Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BinaryExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # <op>
                    CreatePhrase(
                        name="Operator",
                        item=(
                            # Logical
                            "and",          # Logical and
                            "or",           # Logical or
                            "in",           # Collection membership
                            "is",           # Object identity

                            # Function Invocation
                            ".",
                            "->",

                            # Comparison
                            "<",            # Less than
                            "<=",           # Less than or equal to
                            ">",            # Greater than
                            ">=",           # Greater than or equal to
                            "==",           # Equals
                            "!=",           # Not equals

                            # Mathematical
                            "+",            # Addition
                            "-",            # Subtraction
                            "*",            # Multiplication
                            "**",           # Power
                            "/",            # Decimal division
                            "//",           # Integer division
                            "%",            # Modulo

                            # Bit Manipulation
                            "<<",           # Left shift
                            ">>",           # Right shift
                            "^",            # Xor
                            "&",            # Bitwise and
                            "|",            # Bitwise or
                        ),
                    ),

                    # <expr>
                    DynamicPhrasesType.Expressions,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <expr>
            left_node = ExtractDynamic(cast(Node, nodes[0]))
            left_data = cast(ExpressionLexerInfo, GetLexerInfo(left_node))

            # <op>
            operator_leaf = cast(Leaf, ExtractOr(cast(Node, nodes[1])))
            op_value = cast(
                str,
                ExtractToken(
                    operator_leaf,
                    use_match=True,
                ),
            )

            if op_value == "and":
                operator_data = OperatorType.LogicalAnd
            elif op_value == "or":
                operator_data = OperatorType.LogicalOr
            elif op_value == "in":
                operator_data = OperatorType.LogicalIn
            elif op_value == "is":
                operator_data = OperatorType.LogicalIs
            elif op_value == ".":
                operator_data = OperatorType.ChainedFunc
            elif op_value == "->":
                operator_data = OperatorType.ChainedFuncReturnSelf
            elif op_value == "<":
                operator_data = OperatorType.Less
            elif op_value == "<=":
                operator_data = OperatorType.LessEqual
            elif op_value == ">":
                operator_data = OperatorType.Greater
            elif op_value == ">=":
                operator_data = OperatorType.GreaterEqual
            elif op_value == "==":
                operator_data = OperatorType.Equal
            elif op_value == "!=":
                operator_data = OperatorType.NotEqual
            elif op_value == "+":
                operator_data = OperatorType.Add
            elif op_value == "-":
                operator_data = OperatorType.Subtract
            elif op_value == "*":
                operator_data = OperatorType.Multiply
            elif op_value == "**":
                operator_data = OperatorType.Power
            elif op_value == "/":
                operator_data = OperatorType.Divide
            elif op_value == "//":
                operator_data = OperatorType.DivideFloor
            elif op_value == "%":
                operator_data = OperatorType.Modulo
            elif op_value == "<<":
                operator_data = OperatorType.BitShiftLeft
            elif op_value == ">>":
                operator_data = OperatorType.BitShiftRight
            elif op_value == "^":
                operator_data = OperatorType.BitXor
            elif op_value == "&":
                operator_data = OperatorType.BitAnd
            elif op_value == "|":
                operator_data = OperatorType.BitOr
            else:
                assert False, op_value

            # <expr>
            right_node = ExtractDynamic(cast(Node, nodes[2]))
            right_data = cast(ExpressionLexerInfo, GetLexerInfo(right_node))

            SetLexerInfo(
                node,
                BinaryExpressionLexerInfo(
                    BinaryExpressionLexerData(
                        left_data,
                        operator_data,
                        right_data,
                    ),
                    CreateLexerRegions(
                        BinaryExpressionLexerRegions,  # type: ignore
                        node,
                        left_node,
                        operator_leaf,
                        right_node,
                    ),
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
