# ----------------------------------------------------------------------
# |
# |  AsExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-18 14:07:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the AsExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import GrammarDSL
    from ..Common import Tokens as CommonTokens

    from ...GrammarStatement import GrammarStatement


# ----------------------------------------------------------------------
class AsExpression(GrammarStatement):
    """<expr> 'as' <type>"""

    NODE_NAME                               = "As"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(AsExpression, self).__init__(
            GrammarStatement.Type.Expression,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    GrammarDSL.DynamicStatementsType.Expressions,
                    CommonTokens.As,
                    GrammarDSL.DynamicStatementsType.Types,
                ],
                suffers_from_infinite_recursion=True,
            ),
        )
