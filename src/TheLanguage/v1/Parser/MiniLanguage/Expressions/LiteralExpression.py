# ----------------------------------------------------------------------
# |
# |  LiteralExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 22:54:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LiteralExpression object"""

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


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LiteralExpression(Expression):
    type: Type
    value: Any

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(LiteralExpression, self).__init__()

    # ----------------------------------------------------------------------
    @Interface.override
    def EvalType(self) -> Type:
        return self.type

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overrides: Dict[str, Type],
    ) -> Expression.EvalResult:
        return Expression.EvalResult(self.value, self.type, None)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "<<<{}>>>".format(self.value)
