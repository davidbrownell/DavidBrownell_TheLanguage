# ----------------------------------------------------------------------
# |
# |  FuncInvocationNode.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 12:04:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationNodeNode object"""

import os

from enum import auto, Enum
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
    from ..AST import Node, TypeNode


# ----------------------------------------------------------------------
class FunctionCallType(Enum):
    """\
    TODO: Comment
    """

    # Example: obj.Func()
    #              ^^^^^^
    Standard                                = auto()

    # Example: obj.Foo().Bar()
    #                   ^^^^^^
    Chained                                 = auto()

    # Example: obj.Foo()->Bar() == obj.Foo(); obj.Bar()
    #                   ^^^^^^^               ^^^^^^^^^
    Self                                    = auto()

    # Example: obj[0]
    #             ^^^
    Index                                   = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FuncInvocationNode(Node):
    """\
    TODO: Comment
    """

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ArgumentNode(Node):
        """\
        TODO: Comment
        """

        Argument: TypeNode
        Keyword: Optional[str]

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    Flags: Flags.FunctionFlags
    CallType: FunctionCallType

    Name: List[str]
    Arguments: List[ArgumentNode]
