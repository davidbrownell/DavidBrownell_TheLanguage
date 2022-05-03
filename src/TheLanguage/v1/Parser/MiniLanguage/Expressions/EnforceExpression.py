# ----------------------------------------------------------------------
# |
# |  EnforceExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 22:35:10
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
    messages: Optional[List[Expression]]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(EnforceExpression, self).__init__()

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
            if self.messages is None:
                message_suffix = ""
            else:
                suffixes: List[str] = []

                for message in self.messages:
                    suffix = message.Eval(args, type_overrides)
                    suffix = suffix.type.ToStringValue(suffix.value)

                    suffixes.append(suffix)

                message_suffix = ": {}".format(", ".join(suffixes))

            raise ErrorException(
                EnforceError.Create(
                    region=self.expression_region,
                    expression=self.expression.ToString(args),
                    message_suffix=message_suffix,
                ),
            )

        if result.name is not None:
            type_overrides[result.name] = result.type

        return Expression.EvalResult(None, NoneType(), None)

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "Enforce!({}{})".format(
            self.expression.ToString(args),
            "" if not self.messages else ", {}".format(
                ", ".join(message.ToString(args) for message in self.messages),
            ),
        )
