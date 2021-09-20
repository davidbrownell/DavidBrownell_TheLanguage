# ----------------------------------------------------------------------
# |
# |  UnaryExpressionParserInfo.py
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
"""Contains UnaryExpressionParserData, UnaryExpressionParserInfo, and UnaryExpressionParserRegions objects"""

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
class UnaryExpressionParserInfo(ExpressionParserInfo):
    Operator: OperatorType
    Expression: ExpressionParserInfo
