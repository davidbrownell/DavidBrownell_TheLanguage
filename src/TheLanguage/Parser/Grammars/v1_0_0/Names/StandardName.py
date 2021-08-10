# ----------------------------------------------------------------------
# |
# |  StandardName.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:12:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardName object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarPhrase import GrammarPhrase
    from ....Phrases.DSL import CreatePhrase


# ----------------------------------------------------------------------
class StandardName(GrammarPhrase):
    """<name>"""

    NODE_NAME                               = "Standard Name"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(StandardName, self).__init__(
            GrammarPhrase.Type.Name,
            CreatePhrase(
                name=self.NODE_NAME,
                item="TODO",
            ),
        )
