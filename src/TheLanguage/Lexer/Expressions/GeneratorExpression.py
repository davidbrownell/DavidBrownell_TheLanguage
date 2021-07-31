# ----------------------------------------------------------------------
# |
# |  GeneratorExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 13:53:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GeneratorExpression object"""

import os

from typing import Optional

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
class GeneratorExpression(Node):
    """\
    TODO: Comment

    Hypothetical syntax:

        <item_decorator> for <item_var> in <source> [if <condition>]?
    """

    ItemDecorator: Node
    ItemVar: Node
    Source: Node
    Condition: Optional[Node]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(GeneratorExpression, self).__post_init__()

        self.ValidateTypes(
            ItemDecorator=Node.NodeType.Expression,
            ItemVar=Node.NodeType.Expression,
            Source=Node.NodeType.Expression,
            Condition=Node.NodeType.Expression, # TODO: Validate that this is a logical statement
        )
