# ----------------------------------------------------------------------
# |
# |  LambdaExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-07 15:28:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LambdaExpressionParserInfo object"""

import os

from typing import Union

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
    from ..Common.ParametersParserInfo import ParametersParserInfo
    from ..Common.VisitorTools import StackHelper


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LambdaExpressionParserInfo(ExpressionParserInfo):
    """Single-line anonymous function definition"""

    Parameters: Union[
        bool,                               # Should always be False; indicates that no parameters were found
        ParametersParserInfo,               # Non-empty list of parameters
    ]

    Expression: ExpressionParserInfo

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(LambdaExpressionParserInfo, self).__post_init__(regions)

        if isinstance(self.Parameters, bool):
            assert self.Parameters is False, self.Parameters
        else:
            assert self.Parameters

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[self] as helper:
            if isinstance(self.Parameters, ParametersParserInfo):
                with helper["Parameters"]:
                    self.Parameters.Accept(visitor, helper.stack, *args, **kwargs)

            with helper["Expression"]:
                self.Expression.Accept(visitor, helper.stack, *args, **kwargs)
