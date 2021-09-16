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
        BinaryExpressionLexerInfo,
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
            left_info = cast(ExpressionLexerInfo, GetLexerInfo(left_node))

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
                operator_info = OperatorType.LogicalAnd
            elif op_value == "or":
                operator_info = OperatorType.LogicalOr
            elif op_value == "in":
                operator_info = OperatorType.LogicalIn
            elif op_value == "is":
                operator_info = OperatorType.LogicalIs
            elif op_value == ".":
                operator_info = OperatorType.ChainedFunc
            elif op_value == "->":
                operator_info = OperatorType.ChainedFuncReturnSelf
            elif op_value == "<":
                operator_info = OperatorType.Less
            elif op_value == "<=":
                operator_info = OperatorType.LessEqual
            elif op_value == ">":
                operator_info = OperatorType.Greater
            elif op_value == ">=":
                operator_info = OperatorType.GreaterEqual
            elif op_value == "==":
                operator_info = OperatorType.Equal
            elif op_value == "!=":
                operator_info = OperatorType.NotEqual
            elif op_value == "+":
                operator_info = OperatorType.Add
            elif op_value == "-":
                operator_info = OperatorType.Subtract
            elif op_value == "*":
                operator_info = OperatorType.Multiply
            elif op_value == "**":
                operator_info = OperatorType.Power
            elif op_value == "/":
                operator_info = OperatorType.Divide
            elif op_value == "//":
                operator_info = OperatorType.DivideFloor
            elif op_value == "%":
                operator_info = OperatorType.Modulo
            elif op_value == "<<":
                operator_info = OperatorType.BitShiftLeft
            elif op_value == ">>":
                operator_info = OperatorType.BitShiftRight
            elif op_value == "^":
                operator_info = OperatorType.BitXor
            elif op_value == "&":
                operator_info = OperatorType.BitAnd
            elif op_value == "|":
                operator_info = OperatorType.BitOr
            else:
                assert False, op_value

            # <expr>
            right_node = ExtractDynamic(cast(Node, nodes[2]))
            right_info = cast(ExpressionLexerInfo, GetLexerInfo(right_node))

            SetLexerInfo(
                node,
                BinaryExpressionLexerInfo(
                    CreateLexerRegions(node, left_node, operator_leaf, right_node),  # type: ignore
                    left_info,
                    operator_info,
                    right_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
