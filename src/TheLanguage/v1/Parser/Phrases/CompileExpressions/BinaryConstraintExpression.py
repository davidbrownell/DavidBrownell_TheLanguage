# ----------------------------------------------------------------------
# |
# |  BinaryConstraintExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 15:10:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryConstraintExpression object"""

import os

from enum import Enum
from typing import Any, Dict, List

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CompileExpressionPhrase import CompileExpressionPhrase, CompileType

    from ...CompileTypes.Boolean import Boolean
    from ...CompileTypes.Integer import Integer
    from ...CompileTypes.Number import Number

    from ..Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
IncompatibleTypesError                      = CreateError(
    "'{left_value}' ({left_type}) and '{right_value}' ({right_type}) are incompatible types for the '{operator}' operator",
    left_value=str,
    left_type=str,
    right_value=str,
    right_type=str,
    operator=str,
)

IntegerNumberRequiredError                  = CreateError(
    "The operator '{operator}' can only be applied to integers or numbers; '{left_type}' was encountered",
    operator=str,
    left_type=str,
)


IntegerRequiredError                        = CreateError(
    "The operator '{operator}' can only be applied to integers; '{left_type}' was encountered",
    operator=str,
    left_type=str,
)


# ----------------------------------------------------------------------
class OperatorType(Enum):
    Multiply                                = "*"
    Divide                                  = "/"
    DivideFloor                             = "//"
    Modulus                                 = "%"

    Add                                     = "+"
    Subtract                                = "-"

    BitShiftLeft                            = "<<"
    BitShiftRight                           = ">>"

    Less                                    = "<"
    LessEqual                               = "<="
    Greater                                 = ">"
    GreaterEqual                            = ">="

    Equal                                   = "=="
    NotEqual                                = "!="

    BitwiseAnd                              = "&"

    BitwiseXor                              = "^"

    BitwiseOr                               = "|"

    LogicalAnd                              = "and"

    LogicalOr                               = "or"


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryConstraintExpression(CompileExpressionPhrase):
    left: CompileExpressionPhrase
    operator: OperatorType
    right: CompileExpressionPhrase

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(BinaryConstraintExpression, self).__post_init__(regions)

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, CompileType],
    ) -> CompileExpressionPhrase.EvalResult:
        errors: List[Error] = []

        left_result = self.left.Eval(args, type_overloads)

        if self.operator == OperatorType.LogicalAnd:
            if not left_result.type.ToBool(left_result.value):
                return CompileExpressionPhrase.EvalResult(False, Boolean(), None)

            return self.right.Eval(args, type_overloads)

        elif self.operator == OperatorType.LogicalOr:
            if left_result.type.ToBool(left_result.value):
                return left_result

            return self.right.Eval(args, type_overloads)

        else:
            right_result = self.right.Eval(args, type_overloads)

            if left_result.type.name != right_result.type.name:
                errors.append(
                    IncompatibleTypesError.Create(
                        region=self.regions__.self__,
                        left_value=str(left_result.value),
                        left_type=left_result.type.name,
                        right_value=str(right_result.value),
                        right_type=right_result.type.name,
                        operator=self.operator.value,
                    ),
                )

            elif self.operator == OperatorType.Less:
                if left_result.value < right_result.value:
                    return left_result

                return CompileExpressionPhrase.EvalResult(False, Boolean(), None)

            elif self.operator == OperatorType.LessEqual:
                if left_result.value <= right_result.value:
                    return left_result

                return CompileExpressionPhrase.EvalResult(False, Boolean(), None)

            elif self.operator == OperatorType.Greater:
                if left_result.value > right_result.value:
                    return right_result

                return CompileExpressionPhrase.EvalResult(False, Boolean(), None)

            elif self.operator == OperatorType.GreaterEqual:
                if left_result.value >= right_result.value:
                    return right_result

                return CompileExpressionPhrase.EvalResult(False, Boolean(), None)

            elif self.operator == OperatorType.Equal:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value == right_result.value,
                    Boolean(),
                    None,
                )

            elif self.operator == OperatorType.NotEqual:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value != right_result.value,
                    Boolean(),
                    None,
                )

            elif not isinstance(left_result.type, (Integer, Number)):
                errors.append(
                    IntegerNumberRequiredError.Create(
                        region=self.regions__.left,
                        operator=self.operator.value,
                        left_type=left_result.type.name,
                    ),
                )

            elif self.operator == OperatorType.Multiply:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value * right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.Divide:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value / right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.Add:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value + right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.Subtract:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value - right_result.value,
                    left_result.type,
                    None,
                )

            elif not isinstance(left_result.type, Integer):
                errors.append(
                    IntegerRequiredError.Create(
                        region=self.regions__.left,
                        operator=self.operator.value,
                        left_type=left_result.type.name,
                    ),
                )

            elif self.operator == OperatorType.DivideFloor:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value // right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.Modulus:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value % right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.BitShiftLeft:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value << right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.BitShiftRight:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value >> right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.BitwiseAnd:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value & right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.BitwiseXor:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value ^ right_result.value,
                    left_result.type,
                    None,
                )

            elif self.operator == OperatorType.BitwiseOr:
                return CompileExpressionPhrase.EvalResult(
                    left_result.value | right_result.value,
                    left_result.type,
                    None,
                )

            else:
                assert False, self.operator  # pragma: no cover

        assert errors
        raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "{} {} {}".format(
            self.left.ToString(args),
            self.operator.value,
            self.right.ToString(args),
        )
