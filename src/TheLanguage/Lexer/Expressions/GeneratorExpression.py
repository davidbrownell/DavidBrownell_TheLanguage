# ----------------------------------------------------------------------
# |
# |  GeneratorExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 13:53:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GeneratorExpression object"""

import os

from typing import Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..AST import ExpressionNode, VariableNode


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class GeneratorExpression(ExpressionNode):
    """\
    TODO: Comment

    Hypothetical syntax:

        <item_decorator> for <item_var> in <source> [if <condition>]?
    """

    VariableDecorator: ExpressionNode
    Variable: VariableNode
    Source: ExpressionNode
    Condition: Optional[ExpressionNode]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Condition is None or self.Condition.IsBoolean(), self.Condition

    # ----------------------------------------------------------------------
    @Interface.override
    @property
    def ExpressionResultType(self):
        return self.VariableDecorator.ExpressionResultType
