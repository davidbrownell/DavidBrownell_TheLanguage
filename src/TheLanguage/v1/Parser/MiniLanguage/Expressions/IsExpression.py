# ----------------------------------------------------------------------
# |
# |  IsExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 13:41:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IsExpression object"""

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
    from ..Types.BooleanType import BooleanType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IsExpression(Expression):
    expression: Expression
    check_type: Type

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(IsExpression, self).__init__()

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, Type],
    ) -> Expression.EvalResult:
        eval_result = self.expression.Eval(args, type_overloads)

        result, inferred_type = eval_result.type.IsSupportedValueOfType(eval_result.value, self.check_type)

        if inferred_type is not None:
            eval_result.type = inferred_type

            if eval_result.name is not None:
                type_overloads[eval_result.name] = inferred_type

        if result:
            return eval_result

        return Expression.EvalResult(False, BooleanType(), None)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "{} is {}".format(
            self.expression.ToString(args),
            self.check_type.name,
        )
