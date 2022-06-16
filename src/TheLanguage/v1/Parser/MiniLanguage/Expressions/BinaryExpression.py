# ----------------------------------------------------------------------
# |
# |  BinaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 23:38:52
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

from enum import Enum
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

    from ...Error import CreateError, ErrorException, TranslationUnitRegion


# ----------------------------------------------------------------------
class OperatorType(Enum):
    Multiply                                = "*"
    Divide                                  = "/"
    DivideFloor                             = "//"
    Modulus                                 = "%"
    Power                                   = "**"

    Add                                     = "+"
    Subtract                                = "-"

    BitShiftLeft                            = "<<"
    BitShiftRight                           = ">>"

    BitwiseAnd                              = "&"
    BitwiseXor                              = "^"
    BitwiseOr                               = "|"

    Equal                                   = "=="
    NotEqual                                = "!="
    Less                                    = "<"
    LessEqual                               = "<="
    Greater                                 = ">"
    GreaterEqual                            = ">="

    LogicalAnd                              = "and"
    LogicalOr                               = "or"


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
    left_region: TranslationUnitRegion

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(BinaryExpression, self).__init__()

        if self.operator == OperatorType.Multiply:
            eval_type_impl, eval_impl = self._IntegerOrNumberEvalImplFactory(lambda left, right: left * right)
        elif self.operator == OperatorType.Divide:
            eval_type_impl, eval_impl = self._IntegerOrNumberEvalImplFactory(lambda left, right: left / right)
        elif self.operator == OperatorType.DivideFloor:
            eval_type_impl, eval_impl = self._IntegerEvalImplFactory(lambda left, right: left // right)
        elif self.operator == OperatorType.Modulus:
            eval_type_impl, eval_impl = self._IntegerEvalImplFactory(lambda left, right: left % right)
        elif self.operator == OperatorType.Power:
            eval_type_impl, eval_impl = self._IntegerOrNumberEvalImplFactory(lambda left, right: left ** right)
        elif self.operator == OperatorType.Add:
            eval_type_impl, eval_impl = self._IntegerOrNumberEvalImplFactory(lambda left, right: left + right)
        elif self.operator == OperatorType.Subtract:
            eval_type_impl, eval_impl = self._IntegerOrNumberEvalImplFactory(lambda left, right: left - right)
        elif self.operator == OperatorType.BitShiftLeft:
            eval_type_impl, eval_impl = self._IntegerEvalImplFactory(lambda left, right: left << right)
        elif self.operator == OperatorType.BitShiftRight:
            eval_type_impl, eval_impl = self._IntegerEvalImplFactory(lambda left, right: left >> right)
        elif self.operator == OperatorType.BitwiseAnd:
            eval_type_impl, eval_impl = self._IntegerEvalImplFactory(lambda left, right: left & right)
        elif self.operator == OperatorType.BitwiseXor:
            eval_type_impl, eval_impl = self._IntegerEvalImplFactory(lambda left, right: left ^ right)
        elif self.operator == OperatorType.BitwiseOr:
            eval_type_impl, eval_impl = self._IntegerEvalImplFactory(lambda left, right: left | right)
        elif self.operator == OperatorType.Equal:
            eval_type_impl, eval_impl = self._BooleanEvalImplFactory(lambda left, right: left == right)
        elif self.operator == OperatorType.NotEqual:
            eval_type_impl, eval_impl = self._BooleanEvalImplFactory(lambda left, right: left != right)
        elif self.operator == OperatorType.Less:
            eval_type_impl, eval_impl = self._BooleanEvalImplFactory(lambda left, right: left < right)
        elif self.operator == OperatorType.LessEqual:
            eval_type_impl, eval_impl = self._BooleanEvalImplFactory(lambda left, right: left <= right)
        elif self.operator == OperatorType.Greater:
            eval_type_impl, eval_impl = self._BooleanEvalImplFactory(lambda left, right: left > right)
        elif self.operator == OperatorType.GreaterEqual:
            eval_type_impl, eval_impl = self._BooleanEvalImplFactory(lambda left, right: left >= right)
        elif self.operator == OperatorType.LogicalAnd:
            eval_type_impl = self._AndEvalTypeImpl
            eval_impl = self._AndEvalImpl
        elif self.operator == OperatorType.LogicalOr:
            eval_type_impl = self._OrEvalTypeImpl
            eval_impl = self._OrEvalImpl
        else:
            assert False, self.operator  # pragma: no cover

        object.__setattr__(self, "EvalType", eval_type_impl)
        object.__setattr__(self, "Eval", eval_impl)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def EvalType() -> Type:
        raise Exception("This should never be invoked directly, as the implementation will be replaced during instance construction")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def Eval(
        args: Dict[str, Any],
        type_overrides: Dict[str, Type],
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
    def _AndEvalTypeImpl(self):
        right_eval_type = self.right.EvalType()

        if isinstance(right_eval_type, BooleanType):
            return right_eval_type

        return VariantType([BooleanType(), right_eval_type])

    # ----------------------------------------------------------------------
    def _AndEvalImpl(self, args, type_overrides):
        left_result = self.left.Eval(args, type_overrides)

        if not left_result.type.ToBoolValue(left_result.value):
            return Expression.EvalResult(False, BooleanType(), None)

        return self.right.Eval(args, type_overrides)

    # ----------------------------------------------------------------------
    def _OrEvalTypeImpl(self):
        left_type = self.left.EvalType()
        right_type = self.right.EvalType()

        if left_type.name == right_type.name:
            return left_type

        return VariantType([left_type, right_type])

    # ----------------------------------------------------------------------
    def _OrEvalImpl(self, args, type_overrides):
        left_result = self.left.Eval(args, type_overrides)

        if left_result.type.ToBoolValue(left_result.value):
            return left_result

        return self.right.Eval(args, type_overrides)

    # ----------------------------------------------------------------------
    def _IntegerOrNumberEvalImplFactory(
        self,
        eval_func: Callable[[Any, Any], Any],
    ):
        # ----------------------------------------------------------------------
        def EvalType(self):
            left_type = self.left.EvalType()
            right_type = self.right.EvalType()

            if left_type.name != right_type.name:
                raise ErrorException(
                    IncompatibleTypesError.Create(
                        region=self.left_region,
                        left_type=left_type.name,
                        right_type=right_type.name,
                        operator=self.operator.value,
                    ),
                )

            if not isinstance(left_type, (IntegerType, NumberType)):
                raise ErrorException(
                    IntegerOrNumberRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.value,
                        left_type=left_type.name,
                    ),
                )

            return left_type

        # ----------------------------------------------------------------------
        def Eval(self, args, type_overrides):
            left_result = self.left.Eval(args, type_overrides)
            right_result = self.right.Eval(args, type_overrides)

            if left_result.type.name != right_result.type.name:
                raise ErrorException(
                    IncompatibleTypeValuesError.Create(
                        region=self.left_region,
                        left_value=left_result.type.ToStringValue(left_result.type),
                        left_type=left_result.type.name,
                        right_value=right_result.type.ToStringValue(right_result.type),
                        right_type=right_result.type.name,
                        operator=self.operator.value,
                    ),
                )

            if not isinstance(left_result.type, (IntegerType, NumberType)):
                raise ErrorException(
                    IntegerOrNumberRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.value,
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
            types.MethodType(EvalType, self),
            types.MethodType(Eval, self),
        )

    # ----------------------------------------------------------------------
    def _IntegerEvalImplFactory(
        self,
        eval_func: Callable[[Any, Any], Any],
    ):
        # ----------------------------------------------------------------------
        def EvalType(self):
            left_type = self.left.EvalType()
            right_type = self.right.EvalType()

            if left_type.name != right_type.name:
                raise ErrorException(
                    IncompatibleTypesError.Create(
                        region=self.left_region,
                        left_type=left_type.name,
                        right_type=right_type.name,
                        operator=self.operator.value,
                    ),
                )

            if not isinstance(left_type, IntegerType):
                raise ErrorException(
                    IntegerRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.value,
                        left_type=left_type.name,
                    ),
                )

            return left_type

        # ----------------------------------------------------------------------
        def Eval(self, args, type_overrides):
            left_result = self.left.Eval(args, type_overrides)
            right_result = self.right.Eval(args, type_overrides)

            if left_result.type.name != right_result.type.name:
                raise ErrorException(
                    IncompatibleTypeValuesError.Create(
                        region=self.left_region,
                        left_value=left_result.type.ToStringValue(left_result.type),
                        left_type=left_result.type.name,
                        right_value=right_result.type.ToStringValue(right_result.type),
                        right_type=right_result.type.name,
                        operator=self.operator.value,
                    ),
                )

            if not isinstance(left_result.type, IntegerType):
                raise ErrorException(
                    IntegerRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.value,
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
            types.MethodType(EvalType, self),
            types.MethodType(Eval, self),
        )

    # ----------------------------------------------------------------------
    def _BooleanEvalImplFactory(
        self,
        eval_func: Callable[[Any, Any], Any],
    ):
        # ----------------------------------------------------------------------
        def EvalType(self):
            right_type = self.right.EvalType()

            if isinstance(right_type, BooleanType):
                return right_type

            return VariantType([BooleanType(), right_type])

        # ----------------------------------------------------------------------
        def Eval(self, args, type_overrides):
            left_result = self.left.Eval(args, type_overrides)
            right_result = self.right.Eval(args, type_overrides)

            if left_result.type.name != right_result.type.name:
                if isinstance(left_result.type, BooleanType) and not left_result.value:
                    return left_result

                raise ErrorException(
                    IncompatibleTypeValuesError.Create(
                        region=self.left_region,
                        left_value=left_result.type.ToStringValue(left_result.value),
                        left_type=left_result.type.name,
                        right_value=right_result.type.ToStringValue(right_result.value),
                        right_type=right_result.type.name,
                        operator=self.operator.value,
                    ),
                )

            if not eval_func(left_result.value, right_result.value):
                return Expression.EvalResult(False, BooleanType(), None)

            return right_result

        # ----------------------------------------------------------------------

        return (
            types.MethodType(EvalType, self),
            types.MethodType(Eval, self),
        )
