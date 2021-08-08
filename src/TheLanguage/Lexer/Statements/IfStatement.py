# ----------------------------------------------------------------------
# |
# |  IfStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 13:14:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IfStatement object"""

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
    from ..AST import ExpressionNode, StatementNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class IfStatement(StatementNode):
    """\
    TODO: Comment
    """

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ElseIfStatement(StatementNode):
        """\
        TODO: Document
        """

        Condition: ExpressionNode
        Statements: List[StatementNode]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(IfStatement.ElseIfStatement, self).__post_init__()

            assert self.Condition.IsBoolean(), self.Condition

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    Condition: ExpressionNode
    Statements: List[StatementNode]
    ElseIf: Optional[List[ElseIfStatement]]
    ElseStatements: Optional[List[StatementNode]]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(IfStatement, self).__post_init__()

        assert self.Condition.IsBoolean(), self.Condition
