# ----------------------------------------------------------------------
# |
# |  CastExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 10:12:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CastExpression object"""

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
class CastExpression(Node):
    """\
    TODO: Comment
    """

    Expression: Node
    Type: Node

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(CastExpression, self).__post_init__()

        self.ValidateTypes(
            Expression=Node.NodeType.Expression,
            Type=Node.NodeType.Type,
        )
