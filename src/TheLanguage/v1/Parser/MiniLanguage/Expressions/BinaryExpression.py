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

from enum import Enum
from typing import Any, Callable, Dict

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

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

    from ...Error import CreateError, ErrorException
    from ...Region import Region


# TODO: Adjust this

# ----------------------------------------------------------------------
# |  Pubic Types
@dataclass(frozen=True, repr=False)
class Value(ObjectReprImplBase):
    token: str
    precedence: int

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.precedence > 0
        ObjectReprImplBase.__init__(self)



# ----------------------------------------------------------------------
class OperatorType(Enum):
    # ----------------------------------------------------------------------
    # |  Public Data
    Multiply                                = Value.Create("*", 1)
    Divide                                  = Value.Create("/", 1)
    DivideFloor                             = Value.Create("//", 1)
    Modulus                                 = Value.Create("%", 1)

    Add                                     = Value.Create("+", 2)
    Subtract                                = Value.Create("-", 2)

    BitShiftLeft                            = Value.Create("<<", 3)
    BitShiftRight                           = Value.Create(">>", 3)

    Less                                    = Value.Create("<", 4)
    LessEqual                               = Value.Create("<=", 4)
    Greater                                 = Value.Create(">", 4)
    GreaterEqual                            = Value.Create(">=", 4)

    Equal                                   = Value.Create("==", 5)
    NotEqual                                = Value.Create("!=", 5)

    BitwiseAnd                              = Value.Create("&", 6)

    BitwiseXor                              = Value.Create("^", 7)

    BitwiseOr                               = Value.Create("|", 8)

    LogicalAnd                              = Value.Create("and", 9)

    LogicalOr                               = Value.Create("or", 10)


# ----------------------------------------------------------------------
IncompatibleTypesError                      = CreateError(
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
            eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left * right)
        elif self.operator == OperatorType.Divide:
            eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left / right)
        elif self.operator == OperatorType.DivideFloor:
            eval_impl = self._EvalIntegerImplFactory(lambda left, right: left // right)
        elif self.operator == OperatorType.Modulus:
            eval_impl = self._EvalIntegerImplFactory(lambda left, right: left % right)
        elif self.operator == OperatorType.Add:
            eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left + right)
        elif self.operator == OperatorType.Subtract:
            eval_impl = self._EvalIntegerOrNumberImplFactory(lambda left, right: left - right)
        elif self.operator == OperatorType.BitShiftLeft:
            eval_impl = self._EvalIntegerImplFactory(lambda left, right: left << right)
        elif self.operator == OperatorType.BitShiftRight:
            eval_impl = self._EvalIntegerImplFactory(lambda left, right: left >> right)
        elif self.operator == OperatorType.Less:
            eval_impl = self._EvalBoolImplFactory(lambda left, right: left < right)
        elif self.operator == OperatorType.LessEqual:
            eval_impl = self._EvalBoolImplFactory(lambda left, right: left <= right)
        elif self.operator == OperatorType.Greater:
            eval_impl = self._EvalBoolImplFactory(lambda left, right: left > right)
        elif self.operator == OperatorType.GreaterEqual:
            eval_impl = self._EvalBoolImplFactory(lambda left, right: left >= right)
        elif self.operator == OperatorType.Equal:
            eval_impl = self._EvalBoolImplFactory(lambda left, right: left == right)
        elif self.operator == OperatorType.NotEqual:
            eval_impl = self._EvalBoolImplFactory(lambda left, right: left != right)
        elif self.operator == OperatorType.BitwiseAnd:
            eval_impl = self._EvalIntegerImplFactory(lambda left, right: left & right)
        elif self.operator == OperatorType.BitwiseXor:
            eval_impl = self._EvalIntegerImplFactory(lambda left, right: left ^ right)
        elif self.operator == OperatorType.BitwiseOr:
            eval_impl = self._EvalIntegerImplFactory(lambda left, right: left | right)
        elif self.operator == OperatorType.LogicalAnd:
            eval_impl = self._EvalAndImpl
        elif self.operator == OperatorType.LogicalOr:
            eval_impl = self._EvalOrImpl
        else:
            assert False, self.operator  # pragma: no cover

        object.__setattr__(self, "Eval", eval_impl)

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, Type],
    ) -> Expression.EvalResult:
        raise Exception("This should never be invoked directly, as the implementation will be replaced during instane construction")

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
    def _EvalAndImpl(self, args, type_overloads):
        left_result = self.left.Eval(args, type_overloads)

        if not left_result.type.ToBoolValue(left_result.value):
            return Expression.EvalResult(False, BooleanType(), None)

        return self.right.Eval(args, type_overloads)

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
        def Impl(self, args, type_overloads):
            left_result = self.left.Eval(args, type_overloads)
            right_result = self.right.Eval(args, type_overloads)

            if left_result.type.name != right_result.type.name:
                raise ErrorException(
                    IncompatibleTypesError.Create(
                        region=self.left_region,
                        left_value=str(left_result.value),
                        left_type=left_result.type.name,
                        right_value=str(right_result.value),
                        right_type=right_result.type.name,
                        operator=self.operator.token,
                    ),
                )

            if not isinstance(left_result.type, (IntegerType, NumberType)):
                raise ErrorException(
                    IntegerOrNumberRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.token,
                        left_type=left_result.type.name,
                    ),
                )

            return Expression.EvalResult(
                eval_func(left_result.value, right_result.value),
                left_result.type,
                None,
            )

        # ----------------------------------------------------------------------

        return types.MethodType(Impl, self)

    # ----------------------------------------------------------------------
    def _EvalIntegerImplFactory(
        self,
        eval_func: Callable[[int, int], int],
    ):
        # ----------------------------------------------------------------------
        def Impl(self, args, type_overloads):
            left_result = self.left.Eval(args, type_overloads)
            right_result = self.right.Eval(args, type_overloads)

            if left_result.type.name != right_result.type.name:
                raise ErrorException(
                    IncompatibleTypesError.Create(
                        region=self.left_region,
                        left_value=str(left_result.value),
                        left_type=left_result.type.name,
                        right_value=str(right_result.value),
                        right_type=right_result.type.name,
                        operator=self.operator.token,
                    ),
                )

            if not isinstance(left_result.type, IntegerType):
                raise ErrorException(
                    IntegerRequiredError.Create(
                        region=self.left_region,
                        operator=self.operator.token,
                        left_type=left_result.type.name,
                    ),
                )

            return Expression.EvalResult(
                eval_func(left_result.value, right_result.value),
                left_result.type,
                None,
            )

        # ----------------------------------------------------------------------

        return types.MethodType(Impl, self)

    # ----------------------------------------------------------------------
    def _EvalBoolImplFactory(
        self,
        eval_func: Callable[[Any, Any], Any],
    ):
        # ----------------------------------------------------------------------
        def Impl(self, args, type_overloads):
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
                        operator=self.operator.token,
                    ),
                )

            if not eval_func(left_result.value, right_result.value):
                return Expression.EvalResult(False, BooleanType(), None)

            return right_result

        # ----------------------------------------------------------------------

        return types.MethodType(Impl, self)
