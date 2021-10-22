# ----------------------------------------------------------------------
# |
# |  ScopedRefStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 12:55:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ScopedRefStatementParserInfo object"""

import os

from typing import List

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
    from ..Common.VisitorTools import StackHelper, VisitType
    from ..Names.VariableNameParserInfo import VariableNameParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ScopedRefStatementParserInfo(StatementParserInfo):
    Names: List[VariableNameParserInfo]
    Statements: List[StatementParserInfo]

    # ----------------------------------------------------------------------
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnScopedRefStatement(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[self] as helper:
            with helper["Names"]:
                for name in self.Names:
                    name.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["Statements"]:
                for statement in self.Statements:
                    statement.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnScopedRefStatement(stack, VisitType.Exit, self, *args, **kwargs)
