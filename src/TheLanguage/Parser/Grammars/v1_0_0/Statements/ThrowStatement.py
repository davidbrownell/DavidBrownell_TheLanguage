# ----------------------------------------------------------------------
# |
# |  ThrowStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:41:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ThrowStatement object"""

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
    from ....Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
class ThrowStatement(GrammarPhrase):
    """\
    Throws an exception.

    'throw' <expr>?

    Examples:
        throw
        throw foo
        throw (a, b, c)
    """

    NODE_NAME                               = "Throw Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ThrowStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.NODE_NAME,
                item=[
                    "throw",
                    PhraseItem(
                        item=DynamicPhrasesType.Expressions,
                        arity="?",
                    ),
                    CommonTokens.Newline,
                ],
            ),
        )
