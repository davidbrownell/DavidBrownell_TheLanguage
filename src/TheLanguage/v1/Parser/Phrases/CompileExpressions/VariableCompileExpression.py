# ----------------------------------------------------------------------
# |
# |  VariableCompileExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 12:15:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableCompileExpression object"""

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
    from .CompileExpressionPhrase import CompileExpressionPhrase, CompileType
    from ..Error import CreateError, ErrorException


# ----------------------------------------------------------------------
InvalidNameError                            = CreateError(
    "The constraint name '{name}' is not valid",
    name=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableCompileExpression(CompileExpressionPhrase):
    type: CompileType # TODO: Should this be CompileType or CompileTypePhrase?
    name: str

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(VariableCompileExpression, self).__post_init__(regions)

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, CompileType],
    ) -> CompileExpressionPhrase.EvalResult:
        if self.name not in args:
            raise ErrorException(
                InvalidNameError.Create(
                    region=self.regions__.name,
                    name=self.name,
                ),
            )

        return CompileExpressionPhrase.EvalResult(
            args[self.name],
            type_overloads.get(self.name, self.type),
            self.name,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "<<<{}: {}>>>".format(self.name, args[self.name])
