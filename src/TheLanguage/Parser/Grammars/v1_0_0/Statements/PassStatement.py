# ----------------------------------------------------------------------
# |
# |  PassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 16:37:54
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PassStatement object"""

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
class PassStatement(GrammarStatement):
    """pass"""

    NODE_NAME                               = "Pass"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PassStatement, self).__init__(
            GrammarStatement.Type.Statement,
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    CommonTokens.Pass,
                    CommonTokens.Newline,
                ],
            ),
        )
