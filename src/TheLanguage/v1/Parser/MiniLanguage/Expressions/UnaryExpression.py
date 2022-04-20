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
    from ..Types.BooleanType import BooleanType


# ----------------------------------------------------------------------
class OperatorType(Enum):
    Not                                     = "not"

    Positive                                = "+"
    Negative                                = "-"


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryExpression(Expression):
    operator: OperatorType
    expression: Expression

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(UnaryExpression, self).__init__()

        if self.operator == OperatorType.Not:
            eval_impl = self._EvalNotImpl
        else:
            assert False, self.operator

        object.__setattr__(self, "Eval", types.MethodType(eval_impl, self))

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
        return "{} {}".format(
            self.operator.value,
            self.expression.ToString(args),
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _EvalNotImpl(self, args, type_overloads):
        result = self.expression.Eval(args, type_overloads)

        return Expression.EvalResult(
            not result.type.ToBoolValue(result.value),
            BooleanType(),
            None,
        )
