# ----------------------------------------------------------------------
# |
# |  UnaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 13:35:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryExpression object"""

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

    from ...Error import CreateError, ErrorException, Region


# ----------------------------------------------------------------------
# TODO: Errors are no longer showing the operation, just the enum name (e.g. "*" vs "Multiply")
class OperatorType(Enum):
    Not                                     = "not"

    Positive                                = "+"
    Negative                                = "-"


# ----------------------------------------------------------------------
IntegerOrNumberRequiredError                = CreateError(
    "The operator '{operator}' can only be applied to integers or numbers; '{type}' was encountered",
    operator=str,
    type=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryExpression(Expression):
    operator: OperatorType
    expression: Expression
    expression_region: Region

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(UnaryExpression, self).__init__()

        if self.operator == OperatorType.Not:
            eval_type_impl = self._EvalTypeNotImpl
            eval_impl = self._EvalNotImpl
        elif self.operator == OperatorType.Positive:
            eval_type_impl = self._EvalTypeIntegerOrNumberImpl
            eval_impl = self._EvalIntegerOrNumberImplFactory(lambda value: +value)
        elif self.operator == OperatorType.Negative:
            eval_type_impl = self._EvalTypeIntegerOrNumberImpl
            eval_impl = self._EvalIntegerOrNumberImplFactory(lambda value: -value)
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
        return "{} {}".format(
            self.operator.value,
            self.expression.ToString(args),
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _EvalTypeNotImpl(self):
        return BooleanType()

    # ----------------------------------------------------------------------
    def _EvalNotImpl(self, args, type_overloads):
        result = self.expression.Eval(args, type_overloads)

        return Expression.EvalResult(
            not result.type.ToBoolValue(result.value),
            BooleanType(),
            None,
        )

    # ----------------------------------------------------------------------
    def _EvalIntegerOrNumberImplFactory(
        self,
        eval_func: Callable[[Any], Any],
    ):
        # ----------------------------------------------------------------------
        def Impl(self, args, type_overloads):
            result = self.expression.Eval(args, type_overloads)

            if not isinstance(result.type, (IntegerType, NumberType)):
                raise ErrorException(
                    IntegerOrNumberRequiredError.Create(
                        region=self.expression_region,
                        operator=self.operator.name,
                        type=result.type.name,
                    ),
                )

            return Expression.EvalResult(
                eval_func(result.value),
                result.type,
                None,
            )

        # ----------------------------------------------------------------------

        return types.MethodType(Impl, self)

    # ----------------------------------------------------------------------
    def _EvalTypeIntegerOrNumberImpl(self):
        expression_type = self.expression.EvalType()

        if not isinstance(expression_type, (IntegerType, NumberType)):
            raise ErrorException(
                IntegerOrNumberRequiredError.Create(
                    region=self.expression_region,
                    operator=self.operator.name,
                    type=expression_type.name,
                ),
            )

        return expression_type
