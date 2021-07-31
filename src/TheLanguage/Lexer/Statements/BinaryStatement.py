# ----------------------------------------------------------------------
# |
# |  BinaryStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-31 13:02:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryStatement object"""

import os

from enum import IntFlag

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .VariableStatement import VariableStatement

    from ..Common.AST import ExpressionNode, StatementNode
    from ..Common.Flags import OperatorCategory


# ----------------------------------------------------------------------
class BinaryStatementOperator(IntFlag):
    """\
    TODO: Comment
    """

    # Note that the following values should match those found in ../Expressions/BinaryExpression.py
    Add                                     = (OperatorCategory.Math << 8) + 1
    Subtract                                = (OperatorCategory.Math << 8) + 2
    Multiply                                = (OperatorCategory.Math << 8) + 3
    DivideDecimal                           = (OperatorCategory.Math << 8) + 4
    DivideInteger                           = (OperatorCategory.Math << 8) + 5
    Power                                   = (OperatorCategory.Math << 8) + 6
    Modulo                                  = (OperatorCategory.Math << 8) + 7

    BitShiftLeft                            = (OperatorCategory.BitManipulation << 8) + 1
    BitShiftRight                           = (OperatorCategory.BitManipulation << 8) + 2
    BitXor                                  = (OperatorCategory.BitManipulation << 8) + 3
    BitOr                                   = (OperatorCategory.BitManipulation << 8) + 4
    BitAnd                                  = (OperatorCategory.BitManipulation << 8) + 5


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class BinaryStatement(StatementNode):
    """\
    TODO: Comment
    """

    Operator: BinaryStatementOperator
    Variable: VariableStatement
    Right: ExpressionNode
