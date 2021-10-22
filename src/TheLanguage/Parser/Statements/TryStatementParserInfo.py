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
        if visitor.OnTryStatementClause(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[self] as helper:
            with helper["Type"]:
                self.Type.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["Statements"]:
                for statement in self.Statements:
                    statement.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnTryStatementClause(stack, VisitType.Exit, self, *args, **kwargs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TryStatementParserInfo(StatementParserInfo):
    TryStatements: List[StatementParserInfo]
    ExceptClauses: Optional[List[TryStatementClauseParserInfo]]
    DefaultStatements: Optional[List[StatementParserInfo]]

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnTryStatement(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[self] as helper:
            with helper["TryStatements"]:
                for statement in self.TryStatements:
                    statement.Accept(visitor, helper.stack, *args, **kwargs)

            if self.ExceptClauses is not None:
                with helper["ExceptClauses"]:
                    for clause in self.ExceptClauses:
                        clause.Accept(visitor, helper.stack, *args, **kwargs)

            if self.DefaultStatements is not None:
                with helper["DefaultStatements"]:
                    for statement in self.DefaultStatements:
                        statement.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnTryStatement(stack, VisitType.Exit, self, *args, **kwargs)
