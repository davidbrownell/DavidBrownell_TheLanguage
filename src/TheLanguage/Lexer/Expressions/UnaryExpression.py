# ----------------------------------------------------------------------
# |
# |  UnaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 11:11:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryExpression object"""

import os

from dataclasses import dataclass

from enum import IntFlag

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import ExpressionNode
    from ..Common.Flags import OperatorCategory


# ----------------------------------------------------------------------
class UnaryOperator(IntFlag):
    """\
    TODO: Comment
    """

    Not                                     = (OperatorCategory.Logical << 8) + 1

    BitCompliment                           = (OperatorCategory.BitManipulation << 8) + 1


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class UnaryExpression(ExpressionNode):
    """\
    TODO: Comment
    """

    Operator: UnaryOperator
    Expression: ExpressionNode

    # ----------------------------------------------------------------------
    @Interface.override
    def IsBoolean(self) -> bool:
        if self.Operator & OperatorCategory.Logical:
            return True

        return super(UnaryExpression, self).IsBoolean()
