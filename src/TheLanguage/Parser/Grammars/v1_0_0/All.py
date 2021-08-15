# ----------------------------------------------------------------------
# |
# |  All.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:10:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""All grammar phrases for v1.0.0 grammar"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Expressions.BinaryExpression import BinaryExpression
    from .Expressions.CastExpression import CastExpression
    from .Expressions.FuncInvocationExpression import FuncInvocationExpression
    from .Expressions.TernaryExpression import TernaryExpression
    from .Expressions.TupleExpression import TupleExpression
    from .Expressions.UnaryExpression import UnaryExpression
    from .Expressions.VariableExpression import VariableExpression

    from .Names.TupleName import TupleName
    from .Names.VariableName import VariableName

    from .Statements.DeleteStatement import DeleteStatement
    from .Statements.FuncDefinitionStatement import FuncDefinitionStatement
    from .Statements.FuncInvocationStatement import FuncInvocationStatement
    from .Statements.PassStatement import PassStatement
    from .Statements.ReturnStatement import ReturnStatement
    from .Statements.ThrowStatement import ThrowStatement
    from .Statements.VariableDeclarationStatement import VariableDeclarationStatement
    from .Statements.YieldStatement import YieldStatement

    from .Types.FuncType import FuncType
    from .Types.StandardType import StandardType
    from .Types.TupleType import TupleType
    from .Types.VariantType import VariantType


# ----------------------------------------------------------------------
GrammarPhrases                              = [
    # Expressions
    BinaryExpression(),
    CastExpression(),
    FuncInvocationExpression(),
    TernaryExpression(),
    TupleExpression(),
    UnaryExpression(),
    VariableExpression(),

    # Names
    TupleName(),
    VariableName(),

    # Statements
    DeleteStatement(),
    FuncDefinitionStatement(),
    FuncInvocationStatement(),
    PassStatement(),
    ReturnStatement(),
    ThrowStatement(),
    VariableDeclarationStatement(),
    YieldStatement(),

    # Types
    FuncType(),
    StandardType(),
    TupleType(),
    VariantType(),
]
