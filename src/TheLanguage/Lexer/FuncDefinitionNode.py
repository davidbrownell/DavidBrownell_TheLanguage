# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement.py
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
"""Contains the FuncDefinitionStatement object"""

import os

from typing import List

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
class FuncDefinitionStatement(Node):
    """\
    TODO: Comment
    """

    Flags: Flags.FunctionFlags

    Visibility: Flags.VisibilityType

    Name: str
    ReturnType: Node
    Parameters: ParametersNode
    Statements: List[Node]

    # TODO: Add captures

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.Type not in [
            Node.NodeType.Statement,        # Standard function
            Node.NodeType.Expression,       # Lambda
        ]:
            raise Exception("FunctionDefinitionNodes must be a 'Statement' or 'Expression' type")

        self.ValidateTypes(
            ReturnType=Node.NodeType.Type,
            Statements=self.Type,
        )

        # TODO: Visibility should be private for anything other than Standard
        # TODO: Captures should be empty for Standard
