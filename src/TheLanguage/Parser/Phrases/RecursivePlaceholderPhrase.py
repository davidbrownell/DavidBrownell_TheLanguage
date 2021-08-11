# ----------------------------------------------------------------------
# |
# |  RecursivePlaceholderPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-08 23:24:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RecursivePlaceholderPhrase object"""

import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Components.Phrase import Phrase


# ----------------------------------------------------------------------
class RecursivePlaceholderPhrase(Phrase):
    """\
    Temporary Phrase that should be replaced before participating in a Parse hierarchy.

    These objects are used as sentinels within a tree to implement recursive grammars.
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        super(RecursivePlaceholderPhrase, self).__init__("Recursive")

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(
        self,
        *args,  # <unused argument> pylint: disable=W0613
        **kwargs,  # <unused argument> pylint: disable=W0613
    ):  # <parameters differ from overridden> pylint: disable=W0221
        raise Exception("'ParseAsync' should never be called on a RecursivePlaceholderPhrase instance")

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _PopulateRecursiveImpl(
        self,
        new_phrase: Phrase,
    )  -> bool:
        raise Exception("'_PopulateRecursiveImpl' should never be called on a RecursivePlaceholderPhrase instance")
