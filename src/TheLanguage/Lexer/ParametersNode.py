# ----------------------------------------------------------------------
# |
# |  ParametersNode.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 10:37:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ParameterNode and ParametersNode objects"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common.AST import Node


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParameterNode(Node):
    """\
    TODO: Comment
    """

    Name: str
    Type: Node
    DefaultValue: Optional[Node]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(ParameterNode, self).__post_init__()

        self.ValidateTypes(
            Type=Node.NodeType.Type,
            DefaultValue=Node.NodeType.Expression,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParametersNode(Node):
    """\
    TODO: Comment
    """

    Positional: List[ParameterNode]
    Any: List[ParameterNode]
    Keyword: List[ParameterNode]
