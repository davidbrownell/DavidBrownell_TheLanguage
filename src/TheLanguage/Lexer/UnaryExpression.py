# ----------------------------------------------------------------------
# |
# |  UnaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 11:11:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryExpression object"""

import os

from dataclasses import dataclass

from enum import Enum

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
class UnaryOperator(Enum):
    """\
    TODO: Comment
    """

    Not                                     = (OperatorCategory.Logical << 8) + 1

    BitCompliment                           = (OperatorCategory.BitManipulation << 8) + 1


# ----------------------------------------------------------------------
@DataclassDefaultValues(
    Type=Node.NodeType.Expression,  # type: ignore
)
@dataclass(frozen=True)
class UnaryExpression(Node):
    """\
    TODO: Comment
    """

    Operator: UnaryOperator
    Expression: Node

    # ----------------------------------------------------------------------
    def __post_init__(self):
        self.ValidateTypes(
            Expression=Node.NodeType.Expression,
        )
