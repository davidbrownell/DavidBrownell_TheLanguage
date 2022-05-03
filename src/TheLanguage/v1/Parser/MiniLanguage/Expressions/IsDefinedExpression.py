# ----------------------------------------------------------------------
# |
# |  IsDefinedExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 22:50:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IsDefinedExpression object"""

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
    from .VariableExpression import VariableExpression

    from ..Types.BooleanType import BooleanType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IsDefinedExpression(Expression):
    name: Expression

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(IsDefinedExpression, self).__init__()

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def EvalType() -> Type:
        return BooleanType()

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overrides: Dict[str, Type],
    ) -> Expression.EvalResult:
        # If the name is a VariableExpression, don't try to evaluate it as that will generate
        # errors when attempting to return the value of a variable that may not be defined.
        if isinstance(self.name, VariableExpression):
            result = self.name.name
        else:
            result = self.name.Eval(args, type_overrides)
            result = result.type.ToStringValue(result.value)

        return Expression.EvalResult(result in args, BooleanType(), None)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "IsDefined!({})".format(self.name.ToString(args))
