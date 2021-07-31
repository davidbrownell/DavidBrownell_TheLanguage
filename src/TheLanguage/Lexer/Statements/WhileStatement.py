# ----------------------------------------------------------------------
# |
# |  WhileStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 20:05:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the WhileStatement object"""

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
    from ..AST import ExpressionNode, StatementNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class WhileStatement(StatementNode):
    """\
    TODO: Comment
    """

    Condition: ExpressionNode
    Statements: List[StatementNode]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(WhileStatement, self).__post_init__()

        assert self.Condition.IsBoolean(), self.Condition
