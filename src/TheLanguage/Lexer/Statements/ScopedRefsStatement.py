# ----------------------------------------------------------------------
# |
# |  ScopedRefsStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-30 16:47:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ScopedRefsStatement object"""

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
    from ..Common.AST import StatementNode
    from ..Expressions.VariableExpression import VariableExpression


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ScopedRefsStatement(StatementNode):
    """\
    TODO: Comment
    """

    Refs: List[VariableExpression]
    Statements: List[StatementNode]
