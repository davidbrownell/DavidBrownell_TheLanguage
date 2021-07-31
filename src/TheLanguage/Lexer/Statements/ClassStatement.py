# ----------------------------------------------------------------------
# |
# |  ClassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 14:28:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassStatement object"""

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
    from ..AST import StatementNode
    from ..Common import Flags


# ----------------------------------------------------------------------
class ClassType(Enum):
    """\
    TODO: Describe
    """

    Class                                   = auto()
    Interface                               = auto()
    Mixin                                   = auto()
    Exception                               = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ClassStatement(StatementNode):
    """\
    TODO: Describe
    """

    Visibility: Flags.VisibilityType
    Type: ClassType

    # BugBug: Resolve used of Type name vs. StandardType
    Name: str
    BaseClasses: Optional[List[str]]
    Interfaces: Optional[List[str]]
    Mixins: Optional[List[str]]

    Statements: List[StatementNode]

    # TODO: Attributes
