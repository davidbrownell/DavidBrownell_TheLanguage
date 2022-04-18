# ----------------------------------------------------------------------
# |
# |  ErrorStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-17 09:18:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ErrorStatement object"""

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
    from .Statement import Statement, Type


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ErrorStatement(Statement):
    message: str

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(ErrorStatement, self).__init__()

    # ----------------------------------------------------------------------
    @Interface.override
    def Execute(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, Type],
    ) -> Statement.ExecuteResult:
        return Statement.ExecuteResult(
            errors=[self.message],
            warnings=[],
            infos=[],
            should_continue=False,
        )
