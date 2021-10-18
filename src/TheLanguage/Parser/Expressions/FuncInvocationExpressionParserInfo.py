# ----------------------------------------------------------------------
# |
# |  FuncInvocationExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 08:24:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationExpressionParserInfo object"""

import os

from typing import List, Union

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
    from ..Common.ArgumentParserInfo import ArgumentParserInfo
    from ..Common.VisitorTools import StackHelper, VisitType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncInvocationExpressionParserInfo(ExpressionParserInfo):
    Expression: ExpressionParserInfo

    Arguments: Union[
        bool,                               # Should always be False; indicates that no arguments were found
        List[ArgumentParserInfo],           # Non-empty list of arguments
    ]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(FuncInvocationExpressionParserInfo, self).__post_init__(regions)

        if isinstance(self.Arguments, bool):
            assert self.Arguments is False, self.Arguments
        else:
            assert self.Arguments

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnFuncInvocationExpression(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[self] as helper:
            with helper["Expression"]:
                results.append(self.Expression.Accept(visitor, helper.stack, *args, **kwargs))

            if isinstance(self.Arguments, list):
                with helper["Arguments"]:
                    results.append([arg.Accept(visitor, helper.stack, *args, **kwargs) for arg in self.Arguments])

        results.append(visitor.OnFuncInvocationExpression(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
