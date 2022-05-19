# ----------------------------------------------------------------------
# |
# |  ErrorExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 22:45:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ErrorExpression object"""

import os

from typing import Any, Dict, List

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

    from ...Error import CreateError, ErrorException, TranslationUnitRegion


# ----------------------------------------------------------------------
ErrorError                                  = CreateError(
    "{message}",
    message=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ErrorExpression(Expression):
    messages: List[Expression]
    error_region: TranslationUnitRegion

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(ErrorExpression, self).__init__()

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
        raise ErrorException(
            ErrorError.Create(
                region=self.error_region,
                message=self.ToString(args),
            ),
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        results: List[str] = []

        for message in self.messages:
            results.append(message.ToString(args))

        return "Error!({})".format(", ".join(results))
