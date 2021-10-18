# ----------------------------------------------------------------------
# |
# |  TupleExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 08:24:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleExpressionParserInfo object"""

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
    from .ExpressionParserInfo import ExpressionParserInfo
    from ..Common.VisitorTools import StackHelper, VisitType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleExpressionParserInfo(ExpressionParserInfo):
    Expressions: List[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(TupleExpressionParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Expressions"],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnTupleExpression(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[(self, "Expressions")] as helper:
            results.append([expression.Accept(visitor, helper.stack, *args, **kwargs) for expression in self.Expressions])

        results.append(visitor.OnTupleExpression(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
