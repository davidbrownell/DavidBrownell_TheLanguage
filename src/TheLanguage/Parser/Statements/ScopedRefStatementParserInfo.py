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
        results = []

        results.append(visitor.OnScopedRefStatement(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["Names"]:
                results.append([name.Accept(visitor, helper.stack, *args, **kwargs) for name in self.Names])

            with helper["Statements"]:
                results.append([statement.Accept(visitor, helper.stack, *args, **kwargs) for statement in self.Statements])

        results.append(visitor.OnScopedRefStatement(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
