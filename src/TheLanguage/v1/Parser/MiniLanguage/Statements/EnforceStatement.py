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

from typing import Any, Dict, List, Optional

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

    from ...Error import CreateError, Error, ErrorException, Region


# ----------------------------------------------------------------------
EnforceStatementError                       = CreateError(
    "The expression '{expression}' failed{message_suffix}",
    expression=str,
    message_suffix=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class EnforceStatement(Statement):
    expression: Expression
    expression_region: Region
    message: Optional[Expression]

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
        errors: List[Error] = []

        try:
            result = self.expression.Eval(args, type_overloads)

            if not result.type.ToBoolValue(result.value):
                if self.message is None:
                    message_suffix = ""
                else:
                    message_result = self.message.Eval(args, type_overloads)

                    message_suffix = ": {}".format(
                        message_result.type.ToStringValue(message_result.value),
                    )

                errors.append(
                    EnforceStatementError.Create(
                        region=self.expression_region,
                        expression=self.expression.ToString(args),
                        message_suffix=message_suffix,
                    ),
                )

            if result.name is not None:
                type_overloads[result.name] = result.type

        except ErrorException as ex:
            errors += ex.errors

        return Statement.ExecuteResult(
            errors=errors,
            warnings=[],
            infos=[],
            should_continue=not errors,
        )
