# ----------------------------------------------------------------------
# |
# |  All.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-06 08:32:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains statements used in this grammar"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Expressions.AsExpression import AsExpression
    from .Expressions.VariableNameExpression import VariableNameExpression

    from .Statements.FuncDeclarationStatement import FuncDeclarationStatement
    from .Statements.FuncInvocationStatements import FuncInvocationExpression, FuncInvocationStatement
    from .Statements.ImportStatement import ImportStatement
    from .Statements.PassStatement import PassStatement
    from .Statements.VariableDeclarationStatement import VariableDeclarationStatement

    from .Types.StandardType import StandardType
    from .Types.VariantType import VariantType

    from .ClassDeclarationStatement import ClassDeclarationStatement
    from .TupleStatements import TupleExpression, TupleType, TupleVariableDeclarationStatement

# TODO: Check grammar for all statements to determine if syntax errors (bad) or other errors (good)
#       are most appropriate.

# ----------------------------------------------------------------------
Statements                                  = [
    # Statements
    ClassDeclarationStatement(),
    FuncDeclarationStatement(),
    FuncInvocationStatement(),
    ImportStatement(".TheLanguage"),        # TODO: Change this once the language name is finalized
    PassStatement(),
    TupleVariableDeclarationStatement(),
    VariableDeclarationStatement(),

    # Expressions
    AsExpression(),
    FuncInvocationExpression(),
    TupleExpression(),
    VariableNameExpression(),

    # Types
    StandardType(),
    TupleType(),
    VariantType(),
]
