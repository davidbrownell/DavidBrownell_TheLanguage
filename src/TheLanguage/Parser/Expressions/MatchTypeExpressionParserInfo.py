# ----------------------------------------------------------------------
# |
# |  MatchTypeExpressionParserInfo.py
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
"""Contains the MatchTypeExpressionParserData, MatchTypeExpressionParserInfo, and MatchTypeExpressionParserRegions objects"""

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
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeCasePhraseParserInfo(ParserInfo):
    Cases: List[TypeParserInfo]
    Expression: ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class MatchTypeExpressionParserInfo(ExpressionParserInfo):
    Expression: ExpressionParserInfo
    CasePhrases: List[MatchTypeCasePhraseParserInfo]
    Default: Optional[ExpressionParserInfo]
