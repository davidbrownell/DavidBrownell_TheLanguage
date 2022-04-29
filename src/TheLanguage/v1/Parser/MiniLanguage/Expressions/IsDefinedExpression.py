# ----------------------------------------------------------------------
# |
# |  IsDefinedExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-29 07:32:00
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
    from .Expression import Expression
    from ..Types.BooleanType import BooleanType, Type


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
        name = self.name.Eval(args, type_overrides)
        name = name.type.ToStringValue(name.value)

        return Expression.EvalResult(
            name in args,
            BooleanType(),
            None,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        name = self.name.ToString(args)
        return "<<<IsDefined '{}': {}>>>".format(name, name in args)
