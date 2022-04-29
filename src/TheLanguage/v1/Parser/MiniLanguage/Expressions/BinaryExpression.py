# ----------------------------------------------------------------------
# |
# |  BinaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 13:52:11
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryExpression object"""

import os
import types

from enum import auto, Enum
from typing import Any, Callable, Dict

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Expression import Expression, Type

    from ..Types.BooleanType import BooleanType
    from ..Types.IntegerType import IntegerType
    from ..Types.NumberType import NumberType
    from ..Types.VariantType import VariantType

    from ...Error import CreateError, ErrorException, Region


# ----------------------------------------------------------------------
# TODO: Errors are no longer showing the operation, just the enum name (e.g. "*" vs "Multiply")
class OperatorType(Enum):
    # ----------------------------------------------------------------------
    # |  Public Data
    Multiply                                = auto()
    Divide                                  = auto()
    DivideFloor                             = auto()
    Modulus                                 = auto()
    Power                                   = auto()

    Add                                     = auto()
    Subtract                                = auto()

    BitShiftLeft                            = auto()
    BitShiftRight                           = auto()

    BitwiseAnd                              = auto()

    BitwiseXor                              = auto()

    BitwiseOr                               = auto()

    Less                                    = auto()
    LessEqual                               = auto()
    Greater                                 = auto()
    GreaterEqual                            = auto()
    Equal                                   = auto()
    NotEqual                                = auto()

    LogicalAnd                              = auto()

    LogicalOr                               = auto()


# ----------------------------------------------------------------------
IncompatibleTypesError                      = CreateError(
    "'{left_type}' and '{right_type}' are incompatible types when used with the '{operator}' operator",
    left_type=str,
    right_type=str,
    operator=str,
)

IncompatibleTypeValuesError                 = CreateError(
    "'{left_value}' ({left_type}) and '{right_value}' ({right_type}) are incompatible types when used with the '{operator}' operator",
    left_value=str,
    left_type=str,
    right_value=str,
    right_type=str,
    operator=str,
)

IntegerOrNumberRequiredError                = CreateError(
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
@dataclass(frozen=True, repr=False)
class BinaryExpression(Expression):
    left: Expression
    operator: OperatorType
    right: Expression
    left_region: Region

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(BinaryExpression, self).__init__()

        if self.operator == OperatorType.Multiply:
            eval_type_impl, eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left * right)
        elif self.operator == OperatorType.Divide:
            eval_type_impl, eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left / right)
        elif self.operator == OperatorType.DivideFloor:
            eval_type_impl, eval_impl = self._EvalIntegerImplFactory(lambda left, right: left // right)
        elif self.operator == OperatorType.Modulus:
            eval_type_impl, eval_impl = self._EvalIntegerImplFactory(lambda left, right: left % right)
        elif self.operator == OperatorType.Power:
            eval_type_impl, eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left ** right)

        elif self.operator == OperatorType.Add:
            eval_type_impl, eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left + right)
        elif self.operator == OperatorType.Subtract:
            eval_type_impl, eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left - right)

        elif self.operator == OperatorType.BitShiftLeft:
            eval_type_impl, eval_impl = self._EvalIntegerImplFactory(lambda left, right: left << right)
        elif self.operator == OperatorType.BitShiftRight:
            eval_type_impl, eval_impl = self._EvalIntegerImplFactory(lambda left, right: left >> right)

        elif self.operator == OperatorType.BitwiseAnd:
            eval_type_impl, eval_impl = self._EvalIntegerImplFactory(lambda left, right: left & right)

        elif self.operator == OperatorType.BitwiseXor:
            eval_type_impl, eval_impl = self._EvalIntegerImplFactory(lambda left, right: left ^ right)

        elif self.operator == OperatorType.BitwiseOr:
            eval_type_impl, eval_impl = self._EvalIntegerImplFactory(lambda left, right: left | right)

        elif self.operator == OperatorType.Less:
            eval_type_impl, eval_impl = self._EvalBoolImplFactory(lambda left, right: left < right)
        elif self.operator == OperatorType.LessEqual:
            eval_type_impl, eval_impl = self._EvalBoolImplFactory(lambda left, right: left <= right)
        elif self.operator == OperatorType.Greater:
            eval_type_impl, eval_impl = self._EvalBoolImplFactory(lambda left, right: left > right)
        elif self.operator == OperatorType.GreaterEqual:
            eval_type_impl, eval_impl = self._EvalBoolImplFactory(lambda left, right: left >= right)
        elif self.operator == OperatorType.Equal:
            eval_type_impl, eval_impl = self._EvalBoolImplFactory(lambda left, right: left == right)
        elif self.operator == OperatorType.NotEqual:
            eval_type_impl, eval_impl = self._EvalBoolImplFactory(lambda left, right: left != right)

        elif self.operator == OperatorType.LogicalAnd:
            eval_type_impl = self._EvalTypeAndImpl
            eval_impl = self._EvalAndImpl

        elif self.operator == OperatorType.LogicalOr:
            eval_type_impl = self._EvalTypeOrImpl
            eval_impl = self._EvalOrImpl
        else:
            assert False, self.operator  # pragma: no cover

        object.__setattr__(self, "EvalType", eval_type_impl)
        object.__setattr__(self, "Eval", eval_impl)

    # ----------------------------------------------------------------------
    @Interface.override
    def EvalType(self) -> Type:
        raise Exception("This should never be invoked directly, as the implementation will be replaced during instance construction")

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, Type],
    ) -> Expression.EvalResult:
        raise Exception("This should never be invoked directly, as the implementation will be replaced during instance construction")

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

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _EvalTypeAndImpl(self):
        return VariantType([
            BooleanType(),
            self.right.EvalType(),
        ])

    # ----------------------------------------------------------------------
    def _EvalAndImpl(self, args, type_overloads):
        left_result = self.left.Eval(args, type_overloads)

        if not left_result.type.ToBoolValue(left_result.value):
            return Expression.EvalResult(False, BooleanType(), None)

        return self.right.Eval(args, type_overloads)

    # ----------------------------------------------------------------------
    def _EvalTypeOrImpl(self):
        left_type = self.left.EvalType()
        right_type = self.right.EvalType()

        if left_type.name == right_type.name:
            return left_type

        return VariantType([left_type, right_type])

    # ----------------------------------------------------------------------
    def _EvalOrImpl(self, args, type_overloads):
        left_result = self.left.Eval(args, type_overloads)

        if left_result.type.ToBoolValue(left_result.value):
            return left_result

        return self.right.Eval(args, type_overloads)

    # ----------------------------------------------------------------------
    def _EvalIntegerOrNumberImplFactory(
        self,
        eval_func: Callable[[Any, Any], Any],
    ):
        # ----------------------------------------------------------------------
        def EvalTypeImpl(self):
            left_type = self.left.EvalType()
            right_type = self.right.EvalType()

            if left_type.name != right_type.name:
                raise ErrorException(
                    IncompatibleTypesError.Create(
                        region=self.left_region,
                        left_type=left_type.name,
                        right_type=right_type.name,
                        operator=self.operator.name,
                    ),
                )

            if not isinstance(left_type, (IntegerType, NumberType)):
                raise ErrorException(
                    IntegerOrNumberRequiredError.Create(
                        region=self.left_region,
                        oeprator=self.operator.name,
                        left_type=left_type.name,
                    ),
                )

            return left_type

        # ----------------------------------------------------------------------
        def EvalImpl(self, args, type_overloads):
            left_result = self.left.Eval(args, type_overloads)
            right_result = self.right.Eval(args, type_overloads)

            if left_result.type.name != right_result.type.name:
                raise ErrorException(
                    IncompatibleTypeValuesError.Create(
                        region=self.left_region,
                        left_value=str(left_result.value),
                        left_type=left_result.type.name,
                        right_value=str(right_result.value),
                        right_type=right_result.type.name,
                        operator=self.operator.name,
                    ),
                )

            if not isinstance(left_result.type, (IntegerType, NumberType)):
                raise ErrorException(
                    IntegerOrNumberRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.name,
                        left_type=left_result.type.name,
                    ),
                )

            return Expression.EvalResult(
                eval_func(left_result.value, right_result.value),
                left_result.type,
                None,
            )

        # ----------------------------------------------------------------------

        return (
            types.MethodType(EvalTypeImpl, self),
            types.MethodType(EvalImpl, self),
        )

    # ----------------------------------------------------------------------
    def _EvalIntegerImplFactory(
        self,
        eval_func: Callable[[int, int], int],
    ):
        # ----------------------------------------------------------------------
        def EvalTypeImpl(self):
            left_type = self.left.EvalType()
            right_type = self.right.EvalType()

            if left_type.name != right_type.name:
                raise ErrorException(
                    IncompatibleTypesError.Create(
                        region=self.left_region,
                        left_type=left_type.name,
                        right_type=right_type.name,
                        operator=self.operator.name,
                    ),
                )

            if not isinstance(left_type, IntegerType):
                raise ErrorException(
                    IntegerRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.name,
                        left_type=left_type.name,
                    ),
                )

            return left_type

        # ----------------------------------------------------------------------
        def EvalImpl(self, args, type_overloads):
            left_result = self.left.Eval(args, type_overloads)
            right_result = self.right.Eval(args, type_overloads)

            if left_result.type.name != right_result.type.name:
                raise ErrorException(
                    IncompatibleTypeValuesError.Create(
                        region=self.left_region,
                        left_value=str(left_result.value),
                        left_type=left_result.type.name,
                        right_value=str(right_result.value),
                        right_type=right_result.type.name,
                        operator=self.operator.name,
                    ),
                )

            if not isinstance(left_result.type, IntegerType):
                raise ErrorException(
                    IntegerRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.name,
                        left_type=left_result.type.name,
                    ),
                )

            return Expression.EvalResult(
                eval_func(left_result.value, right_result.value),
                left_result.type,
                None,
            )

        # ----------------------------------------------------------------------

        return (
            types.MethodType(EvalTypeImpl, self),
            types.MethodType(EvalImpl, self),
        )

    # ----------------------------------------------------------------------
    def _EvalBoolImplFactory(
        self,
        eval_func: Callable[[Any, Any], Any],
    ):
        # ----------------------------------------------------------------------
        def EvalTypeImpl(self):
            right_type = self.right.EvalType()

            if isinstance(right_type, BooleanType):
                return right_type

            return VariantType([BooleanType(), right_type])

        # ----------------------------------------------------------------------
        def EvalImpl(self, args, type_overloads):
            left_result = self.left.Eval(args, type_overloads)

            if isinstance(left_result.type, BooleanType) and not left_result.value:
                return left_result

            right_result = self.right.Eval(args, type_overloads)

            if left_result.type.name != right_result.type.name:
                raise ErrorException(
                    IncompatibleTypesError.Create(
                        region=self.left_region,
                        left_value=str(left_result.value),
                        left_type=left_result.type.name,
                        right_value=str(right_result.value),
                        right_type=right_result.type.name,
                        operator=self.operator.name,
                    ),
                )

            if not eval_func(left_result.value, right_result.value):
                return Expression.EvalResult(False, BooleanType(), None)

            return right_result

        # ----------------------------------------------------------------------

        return (
            types.MethodType(EvalTypeImpl, self),
            types.MethodType(EvalImpl, self),
        )
