# ----------------------------------------------------------------------
# |
# |  MatchValueExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-14 08:40:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MatchValueExpressionLexerData, MatchValueExpressionLexerInfo, and MatchValueExpressionLexerRegions objects"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionLexerInfo import ExpressionLexerData, ExpressionLexerInfo
    from ..LexerInfo import LexerData, LexerInfo, LexerRegions, Region
    from ..Types.TypeLexerInfo import TypeLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchValueCasePhraseLexerData(LexerData):
    Cases: List[TypeLexerInfo]
    Expression: ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchValueCasePhraseLexerRegions(LexerRegions):
    Cases: Region
    Expression: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchValueCasePhraseLexerInfo(LexerInfo):
    Data: MatchValueCasePhraseLexerData
    Regions: MatchValueCasePhraseLexerRegions


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchValueExpressionLexerData(ExpressionLexerData):
    Expression: ExpressionLexerInfo
    CasePhrases: List[MatchValueCasePhraseLexerInfo]
    Default: Optional[ExpressionLexerInfo]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchValueExpressionLexerRegions(LexerRegions):
    Expression: Region
    CasePhrases: Region
    Default: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchValueExpressionLexerInfo(ExpressionLexerInfo):
    Data: MatchValueExpressionLexerData
    Regions: MatchValueExpressionLexerRegions
