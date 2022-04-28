# ----------------------------------------------------------------------
# |
# |  TernaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 15:22:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpression object"""

import copy
import os

from typing import Any, Dict

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
    from ..Types.VariantType import VariantType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TernaryExpression(Expression):
    condition_expression: Expression
    true_expression: Expression
    false_expression: Expression

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(TernaryExpression, self).__init__()

    # ----------------------------------------------------------------------
    @Interface.override
    def EvalType(self) -> Type:
        # We don't know which type will be the result here, so we need to assume that it can be
        # either.
        true_type = self.true_expression.EvalType()
        false_type = self.false_expression.EvalType()

        if true_type.name == false_type.name:
            return true_type

        return VariantType([true_type, false_type])

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, Type],
    ) -> Expression.EvalResult:
        condition_result = self.condition_expression.Eval(args, type_overloads)

        if condition_result.name is not None:
            type_overloads = copy.deepcopy(type_overloads)

            type_overloads[condition_result.name] = condition_result.type

        if condition_result.type.ToBoolValue(condition_result.value):
            return self.true_expression.Eval(args, type_overloads)

        return self.false_expression.Eval(args, type_overloads)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "{} if {} else {}".format(
            self.true_expression.ToString(args),
            self.condition_expression.ToString(args),
            self.false_expression.ToString(args),
        )
