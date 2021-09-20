# ----------------------------------------------------------------------
# |
# |  BinaryExpressionParserInfo.py
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
"""Contains BinaryExpressionParserData, BinaryExpressionParserRegions, and OperatorType objects"""

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
    from .ExpressionParserInfo import ExpressionParserInfo


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
class BinaryExpressionParserInfo(ExpressionParserInfo):
    Left: ExpressionParserInfo
    Operator: OperatorType
    Right: ExpressionParserInfo
