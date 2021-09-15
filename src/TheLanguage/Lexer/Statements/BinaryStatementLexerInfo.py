# ----------------------------------------------------------------------
# |
# |  BinaryStatementLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-14 08:56:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains BinaryStatementLexerData, BinaryStatementLexerInfo, and BinaryStatementLexerRegions objects"""

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
    from .StatementLexerInfo import StatementLexerData, StatementLexerInfo
    from ..LexerInfo import LexerRegions, Region
    from ..Expressions.ExpressionLexerInfo import ExpressionLexerInfo
    from ..Names.NameLexerInfo import NameLexerInfo


# ----------------------------------------------------------------------
class OperatorType(Enum):
    # Mathematical
    AddInplace                              = auto()
    SubtractInplace                         = auto()
    MultiplyInplace                         = auto()
    PowerInplace                            = auto()
    DivideInplace                           = auto()
    DivideFloorInplace                      = auto()
    ModuloInplace                           = auto()

    # Bit Manipulation
    BitShiftLeftInplace                     = auto()
    BitShiftRightInplace                    = auto()
    BitXorInplace                           = auto()
    BitAndInplace                           = auto()
    BitOrInplace                            = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryStatementLexerData(StatementLexerData):
    Name: NameLexerInfo
    Operator: OperatorType
    Expression: ExpressionLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryStatementLexerRegions(LexerRegions):
    Name: Region
    Operator: Region
    Expression: Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class BinaryStatementLexerInfo(StatementLexerInfo):
    Data: BinaryStatementLexerData
    Regions: BinaryStatementLexerRegions
