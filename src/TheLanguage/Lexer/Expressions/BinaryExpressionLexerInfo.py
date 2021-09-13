# ----------------------------------------------------------------------
# |
# |  BinaryExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 12:42:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains BinaryExpressionLexerData, BinaryExpressionLexerRegions, and OperatorType objects"""

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
    # Logical
    LogicalAnd                              = auto()
    LogicalOr                               = auto()
    LogicalIn                               = auto()
    LogicalIs                               = auto()

    # Function Invocation
    ChainedFunc                             = auto()
    ChainedFuncReturnSelf                   = auto()

    # Comparison
    Less                                    = auto()
    LessEqual                               = auto()
    Greater                                 = auto()
    GreaterEqual                            = auto()
    Equal                                   = auto()
    NotEqual                                = auto()

    # Mathematical
    Add                                     = auto()
    Subtract                                = auto()
    Multiply                                = auto()
    Power                                   = auto()
    Divide                                  = auto()
    DivideFloor                             = auto()
    Modulo                                  = auto()

    # Bit Manipulation
    BitShiftLeft                            = auto()
    BitShiftRight                           = auto()
    BitXor                                  = auto()
    BitAnd                                  = auto()
    BitOr                                   = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryExpressionLexerData(ExpressionLexerData):
    Left: ExpressionLexerInfo
    Operator: OperatorType
    Right: ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryExpressionLexerRegions(LexerRegions):
    Left: Region
    Operator: Region
    Right: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryExpressionLexerInfo(ExpressionLexerInfo):
    Data: BinaryExpressionLexerData
    Regions: BinaryExpressionLexerRegions
