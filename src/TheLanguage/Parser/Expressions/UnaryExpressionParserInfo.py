# ----------------------------------------------------------------------
# |
# |  UnaryExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 17:01:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used when working with Unary expressions"""

import os

from enum import auto, Enum

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
class OperatorType(Enum):
    # Async
    Await                                   = auto()

    # Transfer
    Copy                                    = auto()
    Move                                    = auto()

    # Logical
    Not                                     = auto()

    # Mathematical
    Positive                                = auto()
    Negative                                = auto()

    # Bit Manipulation
    BitCompliment                           = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryExpressionParserInfo(ExpressionParserInfo):
    Operator: OperatorType
    Expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnUnaryExpression(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[(self, "Expression")] as helper:
            self.Expression.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnUnaryExpression(stack, VisitType.Exit, self, *args, **kwargs)
