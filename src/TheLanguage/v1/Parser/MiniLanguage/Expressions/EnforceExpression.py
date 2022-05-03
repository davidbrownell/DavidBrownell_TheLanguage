# ----------------------------------------------------------------------
# |
# |  EnforceExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-30 15:51:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the EnforceExpression object"""

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
    from .Expression import Expression, Type
    from ..Types.NoneType import NoneType

    from ...Error import CreateError, ErrorException, Region


# ----------------------------------------------------------------------
EnforceError                                = CreateError(
    "The expression '{expression}' failed{message_suffix}",
    expression=str,
    message_suffix=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class EnforceExpression(Expression):
    expression: Expression
    expression_region: Region
    message: Optional[Expression]  # TODO: Should be variadic

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def EvalType() -> Type:
        return NoneType()

    # ----------------------------------------------------------------------
    @Interface.override
    def Eval(
        self,
        args: Dict[str, Any],
        type_overrides: Dict[str, Type],
    ) -> Expression.EvalResult:
        result = self.expression.Eval(args, type_overrides)

        if not result.type.ToBoolValue(result.value):
            if self.message is None:
                message_suffix = ""
            else:
                message_result = self.message.Eval(args, type_overrides)

                message_suffix = ": {}".format(
                    message_result.type.ToStringValue(message_result.value),
                )

            raise ErrorException(
                EnforceError.Create(
                    region=self.expression_region,
                    expression=self.expression.ToString(args),
                    message_suffix=message_suffix,
                ),
            )

        if result.name is not None:
            type_overrides[result.name] = result.type

        return Expression.EvalResult(
            None,
            NoneType(),
            None,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "Enforce!({}{})".format(
            self.expression.ToString(args),
            "" if self.message is None else ", {}".format(self.message.ToString(args)),
        )
