# ----------------------------------------------------------------------
# |
# |  AssertStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-26 11:57:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the AssertStatementParserInfo object"""

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
class AssertStatementParserInfo(StatementParserInfo):
    IsEnsure: Optional[bool]
    Expression: ExpressionParserInfo
    DisplayExpression: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(AssertStatementParserInfo, self).__post_init__(regions)
        assert self.IsEnsure is None or self.IsEnsure

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            with helper["Expression"]:
                self.Expression.Accept(visitor, helper.stack, *args, **kwargs)

            if self.DisplayExpression is not None:
                with helper["DisplayExpression"]:
                    self.DisplayExpression.Accept(visitor, helper.stack, *args, **kwargs)