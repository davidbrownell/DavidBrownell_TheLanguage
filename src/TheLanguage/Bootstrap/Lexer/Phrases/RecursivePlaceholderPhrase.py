# ----------------------------------------------------------------------
# |
# |  RecursivePlaceholderPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 22:36:10
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

if True:
    import sys
    sys.path.insert(0, os.path.join(_script_dir, "..", "..", "GeneratedCode"))
    from Lexer_TheLanguage.Phrases_TheLanguage.RecursivePlaceholderPhrase_TheLanguage import *
    sys.path.pop(0)

else:
    with InitRelativeImports():
        from ..Components.Phrase import Phrase


    # ----------------------------------------------------------------------
    class RecursivePlaceholderPhrase(Phrase):
        """\
        Temporary Phrase that should be replaced before participating in Lexing activities.

        Instances of this object are used as sentinels within a Phrase hierarchy to implement
        recursive grammars.
        """

        # ----------------------------------------------------------------------
        def __init__(self):
            super(RecursivePlaceholderPhrase, self).__init__("Recursive")

        # ----------------------------------------------------------------------
        @Interface.override
        async def LexAsync(self, *args, **kwargs):  # <Parameters differ from overridden, unused argument> pylint: disable=W0221, W0613
            raise Exception("This method should never be called on an instance of this object")

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        @Interface.override
        def _PopulateRecursiveImpl(self, *args, **kwargs):  # <Parameters differ from overridden, unused argument> pylint: disable=W0221, W0613
            raise Exception("This method should never be called on an instance of this object")
