# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 14:27:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableDeclarationStatement object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import (
        DynamicStatements,
        GrammarStatement,
        Statement,
    )


# ----------------------------------------------------------------------
class VariableDeclarationStatement(GrammarStatement):
    """\
    Declares a variable.

    <name> = <expression>>
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,
            Statement(
                "Variable Declaration",
                CommonTokens.Name,
                CommonTokens.Equal,
                DynamicStatements.Expressions,
            ),
        )
