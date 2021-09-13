# ----------------------------------------------------------------------
# |
# |  IndexExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-13 10:49:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IndexExpressionLexerData, IndexExpressionLexerInfo, and IndexExpressionLexerRegions objects"""

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
class IndexExpressionLexerData(ExpressionLexerData):
    PrefixExpression: ExpressionLexerInfo
    IndexExpression: ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IndexExpressionLexerRegions(LexerRegions):
    PrefixExpression: Region
    IndexExpression: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IndexExpressionLexerInfo(ExpressionLexerInfo):
    Data: IndexExpressionLexerData
    Regions: IndexExpressionLexerRegions
