# ----------------------------------------------------------------------
# |
# |  FuncDefinitionNode.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 10:29:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncDefinitionNode object"""

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
    from .Common import Flags
    from .ParametersNode import ParametersNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FuncDefinitionNode(Node):
    """\
    TODO: Comment
    """

    Flags: Flags.FunctionFlags

    Visibility: Flags.VisibilityType

    Name: str
    CapturedVars: Optional[List[str]]
    ReturnType: Optional[Node]
    Parameters: ParametersNode
    Statements: List[Node]

    # TODO: Attributes when Type==Statement

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(FuncDefinitionNode, self).__post_init__()

        if self.Type not in [
            Node.NodeType.Statement,        # Standard function
            Node.NodeType.Expression,       # Lambda
        ]:
            raise Exception("FuncDefinitionNodes must be a 'Statement' or 'Expression' type")

        if self.Type == Node.NodeType.Expression:
            if self.Visibility != Flags.VisibilityType.Private:
                raise Exception("'Expression' FuncDefinitionNodes must be 'Private'")

            if len(self.Statements) != 1:
                raise Exception("'Expression' FuncDefinitionNodes must only have a single statement")

        self.ValidateTypes(
            ReturnType=Node.NodeType.Type,
            Statements=self.Type,
        )
