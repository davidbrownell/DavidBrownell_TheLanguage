# ----------------------------------------------------------------------
# |
# |  SmartIfStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 14:22:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SmartIfStatement object"""

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
class SmartIfStatement(StatementNode):
    """\
    TODO: Describe
    """

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ConditionAndStatements(StatementNode):
        """\
        TODO: Describe
        """

        Condition: ExpressionNode
        Statements: List[StatementNode]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            super(SmartIfStatement.ConditionAndStatements, self).__post_init__()

            assert self.Condition.IsBoolean(), self.Condition

    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    Elements: List[ConditionAndStatements]
