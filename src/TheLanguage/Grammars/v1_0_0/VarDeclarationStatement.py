# ----------------------------------------------------------------------
# |
# |  VarDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-10 22:17:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains statements to declare variables"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CommonTokens

    from ..GrammarStatement import DynamicStatements, GrammarStatement, Statement



# ----------------------------------------------------------------------
class VarDeclarationStatement(GrammarStatement):
    """<name> = <expression>"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VarDeclarationStatement, self).__init__(
            GrammarStatement.Type.Statement,

            # ... = <expression>
            Statement(
                "Var Declaration",
                [
                    # '(' <lhs_statement> (',' <lhs_statement>)* ','? ')'
                    Statement(
                        "Tuple",
                        CommonTokens.LParenToken,
                        CommonTokens.PushIgnoreWhitespaceControlToken(),
                        CommonTokens.NameToken,
                        (
                            Statement(
                                "Comma and Statement",
                                CommonTokens.CommaToken,
                                CommonTokens.NameToken,
                            ),
                            0,
                            None,
                        ),
                        (CommonTokens.CommaToken, 0, 1),
                        CommonTokens.PopIgnoreWhitespaceControlToken(),
                        CommonTokens.RParenToken,
                    ),

                    # Standard declaration
                    CommonTokens.NameToken,
                ],
                CommonTokens.EqualToken,
                [
                    DynamicStatements.Expressions,
                    CommonTokens.NameToken,
                ],
            ),
        )
