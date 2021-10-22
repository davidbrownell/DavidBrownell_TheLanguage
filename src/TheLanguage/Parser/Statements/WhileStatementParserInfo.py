# ----------------------------------------------------------------------
# |
# |  WhileStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 12:07:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the WhileStatementParserInfo object"""

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
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class WhileStatementParserInfo(StatementParserInfo):
    Expression: ExpressionParserInfo
    Statements: List[StatementParserInfo]

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnWhileStatement(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[self] as helper:
            with helper["Expression"]:
                self.Expression.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["Statements"]:
                for statement in self.Statements:
                    statement.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnWhileStatement(stack, VisitType.Exit, self, *args, **kwargs)
