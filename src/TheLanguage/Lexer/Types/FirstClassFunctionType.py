# ----------------------------------------------------------------------
# |
# |  FirstClassFunctionType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 21:00:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FirstClassFunctionType object"""

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
    from ..AST import ExpressionNode, Node, TypeNode
    from ..Common import Flags


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FirstClassFunctionType(TypeNode):
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

        Type: TypeNode
        DefaultValue: Optional[ExpressionNode]

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    Flags: Flags.FunctionFlags

    ReturnType: Optional[TypeNode]

    PositionalParameters: Optional[List[ParameterNode]]
    AnyParameters: Optional[List[ParameterNode]]
    KeywordParameters: Optional[List[ParameterNode]]
