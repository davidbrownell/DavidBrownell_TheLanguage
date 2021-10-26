# ----------------------------------------------------------------------
# |
# |  MatchTypeExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 09:06:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types used with MatchTypeExpressions"""

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

    from ..Common.VisitorTools import StackHelper
    from ..ParserInfo import ParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeExpressionClauseParserInfo(ParserInfo):
    Cases: List[TypeParserInfo]
    Expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            with helper["Cases"]:
                for case_type in self.Cases:
                    case_type.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["Expression"]:
                self.Expression.Accept(visitor, helper.stack, *args, **kwargs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeExpressionParserInfo(ExpressionParserInfo):
    Expression: ExpressionParserInfo
    CasePhrases: List[MatchTypeExpressionClauseParserInfo]
    Default: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            with helper["Expression"]:
                self.Expression.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["CasePhrases"]:
                for case_phrase in self.CasePhrases:
                    case_phrase.Accept(visitor, helper.stack, *args, **kwargs)

            if self.Default is not None:
                with helper["Default"]:
                    self.Default.Accept(visitor, helper.stack, *args, **kwargs)
