# ----------------------------------------------------------------------
# |
# |  PrecedenceFunc.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-22 12:08:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PrecedenceFunc. Note that this is defined outside of GrammarPhrase to avoid circular dependencies."""

import os

from typing import Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Lexer.Components.Phrase import Phrase

    from .Expressions.BinaryExpression import BinaryExpression, OperatorType as BinaryOperatorType
    from .Expressions.CallExpression import CallExpression
    from .Expressions.TernaryExpression import TernaryExpression
    from .Expressions.TypeCheckExpression import TypeCheckExpression
    from .Expressions.UnaryExpression import UnaryExpression, OperatorType as UnaryOperatorType


# ----------------------------------------------------------------------
def PrecedenceFunc(
    data: Phrase.LexResultData,
) -> int:
    unary_operator: Optional[UnaryOperatorType] = None
    binary_operator: Optional[BinaryOperatorType] = None

    if data.phrase.name == UnaryExpression.PHRASE_NAME:
        unary_operator = UnaryExpression.GetOperatorType(data)

    if data.phrase.name == BinaryExpression.PHRASE_NAME:
        binary_operator = BinaryExpression.GetOperatorType(data)

    return_value = 10

    for condition_func in [
        ##### - Function call
        # TODO: (This isn't being called, but seems like it should be?): data.phrase.name == CallExpression.PHRASE_NAME,

        #### - Index (TODO)
        #### - Dot (TODO)

        ##### - Positive / Negative
        lambda: unary_operator in [
            UnaryOperatorType.Positive,
            UnaryOperatorType.Negative,
        ],

        ##### - Multiplication / Division
        lambda: binary_operator in [
            BinaryOperatorType.Multiply,
            BinaryOperatorType.Divide,
            BinaryOperatorType.DivideFloor,
            BinaryOperatorType.Modulus,
            BinaryOperatorType.Power,
        ],

        ##### - Addition / Subtraction
        lambda: binary_operator in [
            BinaryOperatorType.Add,
            BinaryOperatorType.Subtract,
        ],

        ##### - BitShift Left / BitShift Right
        lambda: binary_operator in [
            BinaryOperatorType.BitShiftLeft,
            BinaryOperatorType.BitShiftRight,
        ],

        ##### - Bitwise And
        lambda: binary_operator in [
            BinaryOperatorType.BitwiseAnd,
        ],

        ##### - Bitwise Or
        lambda: binary_operator in [
            BinaryOperatorType.BitwiseOr,
        ],

        ##### - Less / Less Equal / Greater / Greater Equal
        ##### - Equal / Not Equal
        ##### - is / is not
        ##### - in / not in (TODO)
        lambda: (
            binary_operator in [
                BinaryOperatorType.Less,
                BinaryOperatorType.LessEqual,
                BinaryOperatorType.Greater,
                BinaryOperatorType.GreaterEqual,
                BinaryOperatorType.Equal,
                BinaryOperatorType.NotEqual,
            ] or data.phrase.name == TypeCheckExpression.PHRASE_NAME
        ),

        ##### - Logical Not
        lambda: unary_operator == UnaryOperatorType.Not,

        ##### - Logical And
        lambda: binary_operator == BinaryOperatorType.LogicalAnd,

        ##### - Logical Or
        lambda: binary_operator == BinaryOperatorType.LogicalOr,

        ##### - in (TODO)
        ##### - not in (TODO)

        ##### - Ternary
        lambda: data.phrase.name == TernaryExpression.PHRASE_NAME,

        ##### - lambda (TODO)
    ]:
        if condition_func():
            return return_value

        return_value += 10

    # if here, we are looking at something unexpected
    assert False, data.phrase.name  # pragma: no cover
