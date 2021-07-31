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
    from .AsExpression import AsExpression
    from .ClassDeclarationStatement import ClassDeclarationStatement
    from .FuncDeclarationStatement import FuncDeclarationStatement
    from .FuncInvocationStatements import FuncInvocationExpression, FuncInvocationStatement
    from .ImportStatement import ImportStatement
    from .PassStatement import PassStatement
    from .StandardType import StandardType
    from .TupleStatements import TupleExpression, TupleType, TupleVariableDeclarationStatement
    from .VariableDeclarationStatement import VariableDeclarationStatement
    from .VariableNameExpression import VariableNameExpression
    from .VariantType import VariantType

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
