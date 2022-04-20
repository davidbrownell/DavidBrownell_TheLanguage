# ----------------------------------------------------------------------
# |
# |  UnaryCompileExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 14:30:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryCompileExpressionParserInfo object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CompileExpressionParserInfo import CompileExpressionParserInfo
    from ...MiniLanguage.Expressions.UnaryExpression import OperatorType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryCompileExpressionParserInfo(CompileExpressionParserInfo):
    operator: OperatorType
    expression: CompileExpressionParserInfo

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(UnaryCompileExpressionParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["expression",],
        )
