# ----------------------------------------------------------------------
# |
# |  TryStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 11:13:11
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TryStatementParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfo, StatementParserInfo
    from ..Common.VisitorTools import StackHelper, VisitType
    from ..Types.TypeParserInfo import TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TryStatementClauseParserInfo(ParserInfo):
    Type: TypeParserInfo
    Name: Optional[str]
    Statements: List[StatementParserInfo]

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnTryStatementClause(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["Type"]:
                results.append(self.Type.Accept(visitor, helper.stack, *args, **kwargs))

            with helper["Statements"]:
                results.append([statement.Accept(visitor, helper.stack, *args, **kwargs) for statement in self.Statements])

        results.append(visitor.OnTryStatementClause(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TryStatementParserInfo(StatementParserInfo):
    TryStatements: List[StatementParserInfo]
    ExceptClauses: Optional[List[TryStatementClauseParserInfo]]
    DefaultStatements: Optional[List[StatementParserInfo]]

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnTryStatement(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["TryStatements"]:
                results.append([statement.Accept(visitor, helper.stack, *args, **kwargs) for statement in self.TryStatements])

            if self.ExceptClauses is not None:
                with helper["ExceptClauses"]:
                    results.append([clause.Accept(visitor, helper.stack, *args, **kwargs) for clause in self.ExceptClauses])

            if self.DefaultStatements is not None:
                with helper["DefaultStatements"]:
                    results.append([statement.Accept(visitor, helper.stack, *args, **kwargs) for statement in self.DefaultStatements])

        results.append(visitor.OnTryStatement(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
