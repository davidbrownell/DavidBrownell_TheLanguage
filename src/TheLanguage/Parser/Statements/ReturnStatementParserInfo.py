# ----------------------------------------------------------------------
# |
# |  ReturnStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 10:04:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ReturnStatementParserInfo object"""

import os

from typing import Optional

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
    from ..Common.VisitorTools import StackHelper
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ReturnStatementParserInfo(StatementParserInfo):
    Expression: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        if self.Expression is not None:
            with StackHelper(stack)[(self, "Expression")] as helper:
                self.Expression.Accept(visitor, helper.stack, *args, **kwargs)
