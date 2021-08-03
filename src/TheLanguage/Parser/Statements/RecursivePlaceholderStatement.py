# ----------------------------------------------------------------------
# |
# |  RecursivePlaceholderStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-15 13:53:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RecursivePlaceholderStatement object"""

import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Components.Statement import Statement


# ----------------------------------------------------------------------
class RecursivePlaceholderStatement(Statement):
    """Temporary Statement that should be replaced before participating in a Parse hierarchy"""

    # ----------------------------------------------------------------------
    def __init__(self):
        super(RecursivePlaceholderStatement, self).__init__("Recursive")

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(
        self,
        *args,                              # pylint: disable=unused-argument
        **kwargs,                           # pylint: disable=unused-argument
    ):  # <Parameters differ> pylint: disable=W0221
        raise Exception("'ParseAsync' should never be called on a RecursivePlaceholderStatement instance")

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_statement: Statement,
    )  -> bool:
        raise Exception("'_PopulateRecursiveImpl' should never be called on a RecursivePlaceholderStatement instance")
