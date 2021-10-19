# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-17 18:33:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationStatementParserInfo object"""

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
    from ..Common.VisitorTools import StackHelper, VisitType
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncInvocationStatementParserInfo(StatementParserInfo):
    Expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnFuncInvocationStatement(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[(self, "Expression")] as helper:
            results.append(self.Expression.Accept(visitor, helper.stack, *args, **kwargs))

        results.append(visitor.OnFuncInvocationStatement(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
