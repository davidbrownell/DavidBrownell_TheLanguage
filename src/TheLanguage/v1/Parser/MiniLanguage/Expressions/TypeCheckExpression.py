# ----------------------------------------------------------------------
# |
# |  TypeCheckExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 14:50:00
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
from typing import Any, Callable, Dict, Optional, Tuple

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
            eval_impl = lambda eval_result: eval_result.type.IsNotSupportedValueOfType
        else:
            assert False, self.operator  # pragma: no cover

        object.__setattr__(self, "Eval", eval_impl)

    # ----------------------------------------------------------------------
    @Interface.override
    def EvalType(self) -> Type:
        # Note that the actual return type is dependent upon the value passed in, which we don't
        # have here. Therefore, we can't reduce the return type at all.
        return self.expression.EvalType()

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
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
        eval_func: Callable[[Type], Callable[[Any, Type], Tuple[Any, Optional[Type]]]]
    ):
        # ----------------------------------------------------------------------
        def Impl(self, args, type_overrides):
            eval_result = self.expression.Eval(args, type_overrides)

            result, inferred_type = eval_func(eval_result.type)(eval_result.value, self.checked_type)

            if inferred_type is not None:
                eval_result.type = inferred_type

                if eval_result.name is not None:
                    type_overrides[eval_result.name] = inferred_type

            if result:
                return eval_result

            return Expression.EvalResult(False, BooleanType(), None)

        # ----------------------------------------------------------------------

        return types.MethodType(Impl, self)
