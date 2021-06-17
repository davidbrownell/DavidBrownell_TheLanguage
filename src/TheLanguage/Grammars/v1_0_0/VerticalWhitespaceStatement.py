# ----------------------------------------------------------------------
# |
# |  VerticalWhitespaceStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-26 07:43:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VerticalWhitespaceStatement object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import Tokens as CommonTokens
    from ..GrammarStatement import GrammarStatement, Statement


# ----------------------------------------------------------------------
class VerticalWhitespaceStatement(GrammarStatement):
    """Eats vertical whitespace"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VerticalWhitespaceStatement, self).__init__(
            GrammarStatement.Type.Statement,
            Statement(
                "Vertical Whitespace",
                CommonTokens.NewlineToken(
                    is_always_ignored=True,
                ),
            ),
        )
