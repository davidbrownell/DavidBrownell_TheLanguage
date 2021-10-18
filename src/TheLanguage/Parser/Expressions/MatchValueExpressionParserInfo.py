# ----------------------------------------------------------------------
# |
# |  MatchValueExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 10:25:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types used with MatchValueExpressions"""

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
    from .ExpressionParserInfo import ExpressionParserInfo
    from ..ParserInfo import ParserInfo
    from ..Common.VisitorTools import StackHelper, VisitType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchValueExpressionClauseParserInfo(ParserInfo):
    Cases: List[ExpressionParserInfo]
    Expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnMatchValueCasePhrase(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["Cases"]:
                results.append([case_value.Accept(visitor, helper.stack, *args, **kwargs) for case_value in self.Cases])

            with helper["Expression"]:
                results.append(self.Expression.Accept(visitor, helper.stack, *args, **kwargs))

        results.append(visitor.OnMatchValueCasePhrase(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchValueExpressionParserInfo(ExpressionParserInfo):
    Expression: ExpressionParserInfo
    CasePhrases: List[MatchValueExpressionClauseParserInfo]
    Default: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnMatchValueExpression(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["Expression"]:
                results.append(self.Expression.Accept(visitor, helper.stack, *args, **kwargs))

            with helper["CasePhrases"]:
                results.append([case_phrase.Accept(visitor, helper.stack, *args, **kwargs) for case_phrase in self.CasePhrases])

            if self.Default is not None:
                with helper["Default"]:
                    results.append(self.Default.Accept(visitor, helper.stack, *args, **kwargs))

        results.append(visitor.OnMatchValueExpression(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
