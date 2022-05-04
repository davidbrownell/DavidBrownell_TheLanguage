# ----------------------------------------------------------------------
# |
# |  TypeCheckExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 23:02:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeCheckExpression object"""

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
    from ..Types.VariantType import VariantType


# ----------------------------------------------------------------------
class OperatorType(Enum):
    Is                                      = "is"
    IsNot                                   = "is not"


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeCheckExpression(Expression):
    operator: OperatorType
    expression: Expression
    check_type: Type

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(TypeCheckExpression, self).__init__()

        if self.operator == OperatorType.Is:
            eval_impl = lambda eval_result: eval_result.type.IsSupportedValueOfType
        elif self.operator == OperatorType.IsNot:
            eval_impl = lambda eval_result: not eval_result.type.IsNotSupportedValueOfType
        else:
            assert False, self.operator  # pragma: no cover

        object.__setattr__(self, "Eval", self._EvalImplFactory(eval_impl))

    # ----------------------------------------------------------------------
    @Interface.override
    def EvalType(self) -> Type:
        expression_type = self.expression.EvalType()

        if isinstance(expression_type, BooleanType):
            return expression_type

        return VariantType([expression_type, BooleanType()])

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
            self.expression.ToString(args),
            self.operator.value,
            self.check_type.name,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _EvalImplFactory(
        self,
        eval_func: Callable[
            [Expression.EvalResult],
            Callable[
                [Any, Type],
                Type.IsSupportedResult,
            ],
        ],
    ):
        # ----------------------------------------------------------------------
        def Eval(self, args, type_overrides):
            eval_result = self.expression.Eval(args, type_overrides)

            is_supported = eval_func(eval_result)(eval_result.value, self.check_type)

            if is_supported.refined_type is not None:
                eval_result.type = is_supported.refined_type

                if eval_result.name is not None:
                    type_overrides[eval_result.name] = is_supported.refined_type

            if is_supported.result:
                # Returning None here causes problems for downstream code. Check for that condition
                # and return a bool to avoid these issues.
                if eval_result.value is None:
                    return Expression.EvalResult(True, BooleanType(), None)

                return eval_result

            return Expression.EvalResult(False, BooleanType(), None)

        # ----------------------------------------------------------------------

        return types.MethodType(Eval, self)
