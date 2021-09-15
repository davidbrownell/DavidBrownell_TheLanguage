# ----------------------------------------------------------------------
# |
# |  MatchTypeExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-13 19:31:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MatchTypeExpressionLexerData, MatchTypeExpressionLexerInfo, and MatchTypeExpressionLexerRegions objects"""

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
class MatchTypeCasePhraseLexerData(LexerData):
    Cases: List[TypeLexerInfo]
    Expression: ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeCasePhraseLexerRegions(LexerRegions):
    Cases: Region
    Expression: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeCasePhraseLexerInfo(LexerInfo):
    Data: MatchTypeCasePhraseLexerData
    Regions: MatchTypeCasePhraseLexerRegions


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeExpressionLexerData(ExpressionLexerData):
    Expression: ExpressionLexerInfo
    CasePhrases: List[MatchTypeCasePhraseLexerInfo]
    Default: Optional[ExpressionLexerInfo]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeExpressionLexerRegions(LexerRegions):
    Expression: Region
    CasePhrases: Region
    Default: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeExpressionLexerInfo(ExpressionLexerInfo):
    Data: MatchTypeExpressionLexerData
    Regions: MatchTypeExpressionLexerRegions
