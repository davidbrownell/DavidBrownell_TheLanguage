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

from enum import Enum

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.DataclassDecorators import DataclassDefaultValues

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.AST import Node
    from .Common.Flags import OperatorCategory


# ----------------------------------------------------------------------
class BinaryOperator(Enum):
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

    Add                                     = (OperatorCategory.Math << 8) + 1
    Subtract                                = (OperatorCategory.Math << 8) + 2
    Multiply                                = (OperatorCategory.Math << 8) + 3
    DivideNumerical                         = (OperatorCategory.Math << 8) + 4
    DivideInteger                           = (OperatorCategory.Math << 8) + 5
    Power                                   = (OperatorCategory.Math << 8) + 6
    Modulo                                  = (OperatorCategory.Math << 8) + 7

    BitShiftLeft                            = (OperatorCategory.BitManipulation << 8) + 1
    BitShiftRight                           = (OperatorCategory.BitManipulation << 8) + 2
    BitXor                                  = (OperatorCategory.BitManipulation << 8) + 3
    BitOr                                   = (OperatorCategory.BitManipulation << 8) + 4
    BitAnd                                  = (OperatorCategory.BitManipulation << 8) + 5


# ----------------------------------------------------------------------
@DataclassDefaultValues(
    Type=Node.NodeType.Expression,  # type: ignore
)
@dataclass(frozen=True)
class BinaryExpression(Node):
    """\
    TODO: Comment
    """

    Operator: BinaryOperator
    Left: Node
    Right: Node

    # ----------------------------------------------------------------------
    def __post_init__(self):
        self.ValidateTypes(
            Left=Node.NodeType.Expression,
            Right=Node.NodeType.Expression,
        )
