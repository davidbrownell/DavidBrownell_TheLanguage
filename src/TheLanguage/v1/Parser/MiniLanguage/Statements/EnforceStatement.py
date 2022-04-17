# ----------------------------------------------------------------------
# |
# |  EnforceStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-17 09:21:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the EnforceStatement object"""

import os

from typing import Any, Dict, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Statement import Statement, Type
    from ..Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class EnforceStatement(Statement):
    expression: Expression
    message: Optional[str]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(EnforceStatement, self).__init__()

    # ----------------------------------------------------------------------
    @Interface.override
    def Execute(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, Type],
    ) -> Statement.ExecuteResult:
        result = self.expression.Eval(args, type_overloads)

        if not result.type.ToBoolValue(result.value):
            return Statement.ExecuteResult(
                errors=[
                    "Expression '{}' failed{}".format(
                        self.expression.ToString(args),
                        "" if self.message is None else ": {}".format(self.message),
                    ),
                ],
                warnings=[],
                infos=[],
                should_continue=False,
            )

        if result.name is not None:
            type_overloads[result.name] = result.type

        return Statement.ExecuteResult(
            errors=[],
            warnings=[],
            infos=[],
            should_continue=True,
        )
