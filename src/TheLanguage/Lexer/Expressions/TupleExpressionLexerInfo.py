# ----------------------------------------------------------------------
# |
# |  TupleExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-13 16:44:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleExpressionLexerData, TupleExpressionLexerInfo, and TupleExpressionLexerRegions objects"""

import os

from typing import List

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
class TupleExpressionLexerData(ExpressionLexerData):
    Expressions: List[ExpressionLexerInfo]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleExpressionLexerRegions(LexerRegions):
    Expressions: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleExpressionLexerInfo(ExpressionLexerInfo):
    Data: TupleExpressionLexerData
    Regions: TupleExpressionLexerRegions
