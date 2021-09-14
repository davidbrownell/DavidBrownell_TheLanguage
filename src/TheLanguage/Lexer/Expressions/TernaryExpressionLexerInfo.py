# ----------------------------------------------------------------------
# |
# |  TernaryExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-13 16:26:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpressionLexerData, TernaryExpressionLexerInfo, and TernaryExpressionLexerRegions objects"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionLexerInfo import ExpressionLexerData, ExpressionLexerInfo
    from ..LexerInfo import LexerRegions, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TernaryExpressionLexerData(ExpressionLexerData):
    TrueExpression: ExpressionLexerInfo
    ConditionExpression: ExpressionLexerInfo
    FalseExpression: ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TernaryExpressionLexerRegions(LexerRegions):
    TrueExpression: Region
    ConditionExpression: Region
    FalseExpression: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TernaryExpressionLexerInfo(ExpressionLexerInfo):
    Data: TernaryExpressionLexerData
    Regions: TernaryExpressionLexerRegions
