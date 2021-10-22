# ----------------------------------------------------------------------
# |
# |  DeleteStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 14:23:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DeleteStatementParserInfo object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import StatementParserInfo
    from ..Common.VisitorTools import VisitType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class DeleteStatementParserInfo(StatementParserInfo):
    VariableName: str

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        visitor.OnDeleteStatement(stack, VisitType.EnterAndExit, self, *args, **kwargs)
