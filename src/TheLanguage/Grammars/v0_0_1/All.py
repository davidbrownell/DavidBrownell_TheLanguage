# ----------------------------------------------------------------------
# |
# |  All.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 08:58:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""All grammar phrases for this grammar"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Lexer.Phrases.DSL import DefaultCommentToken

    # Attributes

    # Expressions
    from .Expressions.BinaryExpression import BinaryExpression
    from .Expressions.FuncInvocationExpression import FuncInvocationExpression
    from .Expressions.GroupExpression import GroupExpression
    from .Expressions.VariableExpression import VariableExpression

    # Names
    from .Names.VariableName import VariableName

    # Statements
    from .Statements.PassStatement import PassStatement
    from .Statements.VariableDeclarationStatement import VariableDeclarationStatement

    # Types
    from .Types.StandardType import StandardType


# ----------------------------------------------------------------------
GrammarCommentToken                         = DefaultCommentToken

GrammarPhrases                              = [
    # Attributes

    # Expressions
    BinaryExpression(),
    FuncInvocationExpression(),
    GroupExpression(),
    VariableExpression(),

    # Names
    VariableName(),

    # Statements
    PassStatement(),
    VariableDeclarationStatement(),

    # Types
    StandardType(),
]
