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

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.ParserInterfaces.Expressions.BinaryExpressionLexerInfo import (
        BinaryExpressionLexerData,
        BinaryExpressionLexerInfo,
        BinaryExpressionLexerRegions,
        ExpressionLexerInfo,
        OperatorType,
    )

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

            # <op>
            op_leaf = cast(Leaf, ExtractOr(cast(Node, nodes[1])))
            op_value = cast(
                str,
                ExtractToken(
                    op_leaf,
                    use_match=True,
                ),
            )

            if op_value == "and":
                operator_type = OperatorType.LogicalAnd
            elif op_value == "or":
                operator_type = OperatorType.LogicalOr
            elif op_value == "in":
                operator_type = OperatorType.LogicalIn
            elif op_value == "is":
                operator_type = OperatorType.LogicalIs
            elif op_value == ".":
                operator_type = OperatorType.ChainedFunc
            elif op_value == "->":
                operator_type = OperatorType.ChainedFuncReturnSelf
            elif op_value == "<":
                operator_type = OperatorType.Less
            elif op_value == "<=":
                operator_type = OperatorType.LessEqual
            elif op_value == ">":
                operator_type = OperatorType.Greater
            elif op_value == ">=":
                operator_type = OperatorType.GreaterEqual
            elif op_value == "==":
                operator_type = OperatorType.Equal
            elif op_value == "!=":
                operator_type = OperatorType.NotEqual
            elif op_value == "+":
                operator_type = OperatorType.Add
            elif op_value == "-":
                operator_type = OperatorType.Subtract
            elif op_value == "*":
                operator_type = OperatorType.Multiply
            elif op_value == "**":
                operator_type = OperatorType.Power
            elif op_value == "/":
                operator_type = OperatorType.Divide
            elif op_value == "//":
                operator_type = OperatorType.DivideFloor
            elif op_value == "%":
                operator_type = OperatorType.Modulo
            elif op_value == "<<":
                operator_type = OperatorType.BitShiftLeft
            elif op_value == ">>":
                operator_type = OperatorType.BitShiftRight
            elif op_value == "^":
                operator_type = OperatorType.BitXor
            elif op_value == "&":
                operator_type = OperatorType.BitAnd
            elif op_value == "|":
                operator_type = OperatorType.BitOr
            else:
                assert False, op_value

            # <expr>
            right_node = ExtractDynamic(cast(Node, nodes[2]))

            SetLexerInfo(
                node,
                BinaryExpressionLexerInfo(
                    BinaryExpressionLexerData(
                        cast(ExpressionLexerInfo, GetLexerInfo(left_node)),
                        operator_type,
                        cast(ExpressionLexerInfo, GetLexerInfo(right_node)),
                    ),
                    CreateLexerRegions(
                        BinaryExpressionLexerRegions,  # type: ignore
                        node,
                        left_node,
                        op_leaf,
                        right_node,
                    ),
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
