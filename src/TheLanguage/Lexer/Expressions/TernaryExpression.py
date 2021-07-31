# ----------------------------------------------------------------------
# |
# |  TernaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 10:16:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpression object"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.DataclassDecorators import DataclassDefaultValues

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.AST import Node


# ----------------------------------------------------------------------
@DataclassDefaultValues(
    Type=Node.NodeType.Expression,  # type: ignore
)
@dataclass(frozen=True)
class TernaryExpression(Node):
    """\
    TODO: Comment
    """

    Condition: Node
    TrueNode: Node
    FalseNode: Node

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(TernaryExpression, self).__post_init__()

        self.ValidateTypes(
            Condition=Node.NodeType.Expression,
            TrueNode=Node.NodeType.Expression,
            FalseNode=Node.NodeType.Expression,
        )
