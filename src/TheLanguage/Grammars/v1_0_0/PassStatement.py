# ----------------------------------------------------------------------
# |
# |  PassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-13 15:18:08
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
    from .Common import Tokens as CommonTokens
    from ..GrammarStatement import GrammarStatement, Statement


# ----------------------------------------------------------------------
class PassStatement(GrammarStatement):
    """'pass'"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PassStatement, self).__init__(
            GrammarStatement.Type.Statement,
            Statement("Pass", CommonTokens.Pass),
        )
