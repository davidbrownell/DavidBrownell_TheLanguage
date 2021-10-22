# ----------------------------------------------------------------------
# |
# |  TernaryExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 16:45:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpressionParserInfo object"""

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
    from .ExpressionParserInfo import ExpressionParserInfo
    from ..Common.VisitorTools import StackHelper, VisitType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TernaryExpressionParserInfo(ExpressionParserInfo):
    ConditionExpression: ExpressionParserInfo
    TrueExpression: ExpressionParserInfo
    FalseExpression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnTernaryExpression(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[self] as helper:
            with helper["ConditionExpression"]:
                self.ConditionExpression.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["TrueExpression"]:
                self.TrueExpression.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["FalseExpression"]:
                self.FalseExpression.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnTernaryExpression(stack, VisitType.Exit, self, *args, **kwargs)
