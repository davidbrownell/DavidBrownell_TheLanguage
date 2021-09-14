# ----------------------------------------------------------------------
# |
# |  UnaryExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-13 18:54:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains UnaryExpressionLexerData, UnaryExpressionLexerInfo, and UnaryExpressionLexerRegions objects"""

import os

from enum import auto, Enum

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
class OperatorType(Enum):
    # Coroutine
    Await                                   = auto()

    # Transfer
    Copy                                    = auto()
    Move                                    = auto()

    # Logical
    Not                                     = auto()

    # Mathematical
    Positive                                = auto()
    Negative                                = auto()

    # Bit Manipulation
    BitCompliment                           = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryEpressionLexerData(ExpressionLexerData):
    Operator: OperatorType
    Expression: ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryExpressionLexerRegions(LexerRegions):
    Operator: Region
    Expression: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class UnaryExpressionLexerInfo(ExpressionLexerInfo):
    Data: UnaryEpressionLexerData
    Regions: UnaryExpressionLexerRegions
