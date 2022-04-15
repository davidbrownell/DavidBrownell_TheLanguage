# ----------------------------------------------------------------------
# |
# |  LiteralConstraintExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 14:34:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LiteralConstraintExpression object"""

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


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LiteralConstraintExpression(ConstraintExpressionPhrase):
    type: CompileTimeType
    value: Any

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(LiteralConstraintExpression, self).__post_init__(regions)

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, CompileTimeType],
    ) -> ConstraintExpressionPhrase.EvalResult:
        return ConstraintExpressionPhrase.EvalResult(
            self.value,
            self.type,
            None,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "<<<{}>>>".format(self.value)
