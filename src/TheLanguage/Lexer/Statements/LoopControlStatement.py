# ----------------------------------------------------------------------
# |
# |  LoopControlStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 16:58:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LoopControlStatement object"""

import os
from enum import auto, Enum

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.AST import StatementNode


# ----------------------------------------------------------------------
class LoopControlType(Enum):
    """\
    TODO: Comment
    """

    Break                                   = auto()
    Continue                                = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class LoopControlStatement(StatementNode):
    """\
    TODO: Comment
    """

    ControlType: LoopControlType
