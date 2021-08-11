# ----------------------------------------------------------------------
# |
# |  BinaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 10:38:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryExpression object"""

import os

from enum import IntFlag

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import ExpressionNode
    from ..Common.Flags import OperatorCategory


# ----------------------------------------------------------------------
class BinaryExpressionOperator(IntFlag):
    """\
    TODO: Comment
    """

    And                                     = (OperatorCategory.Logical << 8) + 1
    Or                                      = (OperatorCategory.Logical << 8) + 2
    In                                      = (OperatorCategory.Logical << 8) + 3
    Is                                      = (OperatorCategory.Logical << 8) + 4

    Less                                    = (OperatorCategory.Comparison << 8) + 1
    LessEqual                               = (OperatorCategory.Comparison << 8) + 2
    Greater                                 = (OperatorCategory.Comparison << 8) + 3
    GreaterEqual                            = (OperatorCategory.Comparison << 8) + 4
    Equal                                   = (OperatorCategory.Comparison << 8) + 5
    NotEqual                                = (OperatorCategory.Comparison << 8) + 6

    # Note that the following values should match those found in ../Statements/BinaryStatement.py
    Add                                     = (OperatorCategory.Math << 8) + 1
    Subtract                                = (OperatorCategory.Math << 8) + 2
    Multiply                                = (OperatorCategory.Math << 8) + 3
    DivideDecimal                           = (OperatorCategory.Math << 8) + 4
    DivideInteger                           = (OperatorCategory.Math << 8) + 5
    Power                                   = (OperatorCategory.Math << 8) + 6
    Modulo                                  = (OperatorCategory.Math << 8) + 7

    BitShiftLeft                            = (OperatorCategory.BitManipulation << 8) + 1
    BitShiftRight                           = (OperatorCategory.BitManipulation << 8) + 2
    BitXor                                  = (OperatorCategory.BitManipulation << 8) + 3
    BitOr                                   = (OperatorCategory.BitManipulation << 8) + 4
    BitAnd                                  = (OperatorCategory.BitManipulation << 8) + 5


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class BinaryExpression(ExpressionNode):
    """\
    TODO: Comment
    """

    Operator: BinaryExpressionOperator
    Left: ExpressionNode
    Right: ExpressionNode

    # BugBug: Verify that the method can handle the right expression type

    # ----------------------------------------------------------------------
    @Interface.override
    @property
    def ExpressionResultType(self):
        return None # BugBug
