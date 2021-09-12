# ----------------------------------------------------------------------
# |
# |  ArgumentLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-12 10:20:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ArgumentLexerData, ArgumentLexerInfo, and ArgumentLexerRegions items"""

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
    from ..LexerInfo import LexerData, LexerInfo, LexerRegions, Region
    from ..Expressions.ExpressionLexerInfo import ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ArgumentLexerData(LexerData):
    Expression: ExpressionLexerInfo
    Keyword: Optional[str]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ArgumentLexerRegions(LexerRegions):
    Expression: Region
    Keyword: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ArgumentLexerInfo(LexerInfo):
    Data: ArgumentLexerData
    Regions: ArgumentLexerRegions
