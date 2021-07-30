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

from typing import List

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
    from .Common import Flags


# ----------------------------------------------------------------------
@DataclassDefaultValues(
    Type=Node.NodeType.Type,  # type: ignore
)
@dataclass(frozen=True)
class FirstClassFunctionType(Node):
    """\
    TODO: Comment
    """

    Flags: Flags.FunctionFlags

    Name: str
    ReturnType: Node
    Parameters: List[Node]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        self.ValidateTypes(
            ReturnType=Node.NodeType.Type,
            Parameters=Node.NodeType.Type,
        )
