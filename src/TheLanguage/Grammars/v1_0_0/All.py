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
    from .CommentStatement import CommentStatement
    from .FuncDeclarationStatement import FuncDeclarationStatement
    from .FuncInvocationHybrid import FuncInvocationHybrid
    from .ImportStatement import ImportStatement
    from .PassStatement import PassStatement
    from .VariableDeclarationStatement import VariableDeclarationStatement
    from .VariableNameExpression import VariableNameExpression
    from .VerticalWhitespaceStatement import VerticalWhitespaceStatement


# ----------------------------------------------------------------------
Statements                                  = [
    # Statements
    ImportStatement(".TheLanguage"),        # TODO: Update this when the name is finalized
    FuncDeclarationStatement(),
    VariableDeclarationStatement(),

    PassStatement(),
    CommentStatement(),
    VerticalWhitespaceStatement(),

    # Hybrid
    FuncInvocationHybrid(),

    # Expressions
    VariableNameExpression(),
]
