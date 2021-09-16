# ----------------------------------------------------------------------
# |
# |  LambdaExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-13 14:42:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LambdaExpressionLexerData, LambdaExpressionLexerInfo, and LambdaExpressionLexerRegions objects"""

import os

from typing import Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionLexerInfo import ExpressionLexerInfo
    from ..Common.ParametersLexerInfo import ParametersLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LambdaExpressionLexerInfo(ExpressionLexerInfo):
    Parameters: Optional[ParametersLexerInfo]
    Expression: ExpressionLexerInfo
