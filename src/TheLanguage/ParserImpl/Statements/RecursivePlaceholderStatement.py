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

from typing import List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Statement import Statement


# ----------------------------------------------------------------------
class RecursivePlaceholderStatement(Statement):
    """Temporary Statement that should be replaced before participating in a Parse hierarchy"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        unique_id: Optional[List[str]]=None,
        type_id: Optional[int]=None,
    ):
        super(RecursivePlaceholderStatement, self).__init__("Placeholder")

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        unique_id: List[str],
    ) -> Statement:
        return self.CloneImpl(
            unique_id=unique_id,
            type_id=self.TypeId,
        )

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
    def PopulateRecursiveImpl(
        self,
        new_statement: Statement,
    )  -> bool:
        raise Exception("'PopulateRecursiveImpl' should never be called on a RecursivePlaceholderStatement instance")
