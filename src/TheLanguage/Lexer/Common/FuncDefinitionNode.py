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
    from . import Flags
    from ..AST import Node, ExpressionNode, TypeNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FuncDefinitionNode(Node):
    """\
    TODO: Comment
    """

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ParameterNode(Node):
        """\
        TODO: Comment
        """

        Name: str
        Type: TypeNode
        DefaultValue: Optional[ExpressionNode]

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    Flags: Flags.FunctionFlags

    Name: str
    CapturedVars: Optional[List[str]]
    ReturnType: Optional[Node]

    PositionalParameters: Optional[List[ParameterNode]]
    AnyParameters: Optional[List[ParameterNode]]
    KeywordParameters: Optional[List[ParameterNode]]

    # TODO: Attributes when Type==Statement
