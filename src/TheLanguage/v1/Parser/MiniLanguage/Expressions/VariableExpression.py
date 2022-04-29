# ----------------------------------------------------------------------
# |
# |  VariableExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 13:23:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableExpression object"""

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

    from ...Error import CreateError, ErrorException
    from ...Region import Region


# ----------------------------------------------------------------------
InvalidNameError                            = CreateError(
    "'{name}' is not defined",
    name=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableExpression(Expression):
    type: Type
    name: str
    name_region: Region

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(VariableExpression, self).__init__()

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
        if self.name not in args:
            raise ErrorException(
                InvalidNameError.Create(
                    region=self.name_region,
                    name=self.name,
                ),
            )

        return Expression.EvalResult(
            args[self.name],
            type_overrides.get(self.name, self.type),
            self.name,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ToString(
        self,
        args: Dict[str, Any],
    ) -> str:
        return "<<<{}: {}>>>".format(self.name, args[self.name])
