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
    # TODO from .ClassDeclarationStatement import ClassDeclarationStatement
    # TODO from .FuncDeclarationStatement import FuncDeclarationStatement
    # TODO from .FuncInvocationStatements import FuncInvocationExpression, FuncInvocationStatement
    # TODO from .ImportStatement import ImportStatement
    # TODO from .PassStatement import PassStatement
    # TODO from .TupleStatements import TupleExpression, TupleVariableDeclarationStatement
    # TODO from .VariableDeclarationStatement import VariableDeclarationStatement
    # TODO from .VariableNameExpression import VariableNameExpression
    # TODO from .VerticalWhitespaceStatement import VerticalWhitespaceStatement
    pass

# ----------------------------------------------------------------------
Statements                                  = [
    # TODO # Statements
    # TODO ClassDeclarationStatement(),
    # TODO FuncDeclarationStatement(),
    # TODO FuncInvocationStatement(),
    # TODO ImportStatement(".TheLanguage"),        # TODO: Update this when the name is finalized
    # TODO TupleVariableDeclarationStatement(),
    # TODO VariableDeclarationStatement(),
    # TODO
    # TODO PassStatement(),
    # TODO
    # TODO # Expressions
    # TODO FuncInvocationExpression(),
    # TODO TupleExpression(),
    # TODO VariableNameExpression(),
]
