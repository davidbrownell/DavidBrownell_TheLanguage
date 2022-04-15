# ----------------------------------------------------------------------
# |
# |  IsNotConstraintExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 14:56:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IsNotConstraintExpression object"""

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
    from .ConstraintExpressionPhrase import CompileTimeType, ConstraintExpressionPhrase
    from ..Common.CompileTimeTypes.Boolean import Boolean


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IsNotConstraintExpression(ConstraintExpressionPhrase):
    expression: ConstraintExpressionPhrase
    check_type: CompileTimeType

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(IsNotConstraintExpression, self).__post_init__(regions)

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, CompileTimeType],
    ) -> ConstraintExpressionPhrase.EvalResult:
        result = self.expression.Eval(args, type_overloads)

        type_check_result = result.type.IsNotSupportedAndOfType(result.value, self.check_type)

        if result.name is not None and type_check_result[1] is not None:
            type_overloads[result.name] = type_check_result[1]

        if type_check_result[0]:
            return result

        return ConstraintExpressionPhrase.EvalResult(False, Boolean(), None)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "{} is not {}".format(
            self.expression.ToString(args),
            self.check_type.name,
        )
