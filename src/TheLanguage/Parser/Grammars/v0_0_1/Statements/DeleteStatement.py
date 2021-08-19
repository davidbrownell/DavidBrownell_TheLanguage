# ----------------------------------------------------------------------
# |
# |  DeleteStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 16:44:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DeleteStatement object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import GrammarPhrase
    from ....Phrases.DSL import CreatePhrase, DynamicPhrasesType


# ----------------------------------------------------------------------
class DeleteStatement(GrammarPhrase):
    """\
    Deletes a variable so that it is no longer accessible.

    'del' <name>

    Examples:
        del foo
        del bar
    """

    PHRASE_NAME                             = "Delete Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(DeleteStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "del",
                    DynamicPhrasesType.Names,
                    CommonTokens.Newline,
                ],
            ),
        )
