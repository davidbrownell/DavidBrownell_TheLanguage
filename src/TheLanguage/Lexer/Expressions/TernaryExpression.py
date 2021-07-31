# ----------------------------------------------------------------------
# |
# |  TernaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 10:16:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpression object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.AST import ExpressionNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TernaryExpression(ExpressionNode):
    """\
    TODO: Comment
    """

    Condition: ExpressionNode
    TrueNode: ExpressionNode
    FalseNode: ExpressionNode

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(TernaryExpression, self).__post_init__()

        assert self.Condition.IsBoolean(), self.Condition
