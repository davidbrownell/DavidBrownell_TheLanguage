# ----------------------------------------------------------------------
# |
# |  WhileStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 16:17:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the WhileStatement object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import StatementsPhraseItem
    from ...GrammarPhrase import GrammarPhrase
    from ....Parser.Phrases.DSL import CreatePhrase, DynamicPhrasesType


# ----------------------------------------------------------------------
class WhileStatement(GrammarPhrase):
    """\
    Exectues statements while a condition is true.

    'while' <expr> ':'
        <statement>+

    Examples:
        while Func1():
            pass

        while one and two:
            pass
    """

    PHRASE_NAME                             = "While Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(WhileStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'while'
                    "while",

                    # <expr>
                    DynamicPhrasesType.Expressions,

                    StatementsPhraseItem.Create(),
                ],
            ),
        )
