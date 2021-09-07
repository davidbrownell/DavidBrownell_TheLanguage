# ----------------------------------------------------------------------
# |
# |  RaiseStatement.py
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
"""Contains the RaiseStatement object"""

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
    from ....Parser.Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
class RaiseStatement(GrammarPhrase):
    """\
    Raises an exception.

    'raise' <expr>?

    Examples:
        raise
        raise foo
        raise (a, b, c)
    """

    PHRASE_NAME                             = "Raise Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(RaiseStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "raise",
                    PhraseItem(
                        item=DynamicPhrasesType.Expressions,
                        arity="?",
                    ),
                    CommonTokens.Newline,
                ],
            ),
        )
