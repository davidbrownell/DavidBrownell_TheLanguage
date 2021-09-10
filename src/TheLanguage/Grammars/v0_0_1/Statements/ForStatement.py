# ----------------------------------------------------------------------
# |
# |  ForStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-17 22:39:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ForStatement object"""

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
class ForStatement(GrammarPhrase):
    """\
    Statement that exercises an iterator.

    'for' <name> 'in' <expr> ':'
        <statement>+

    Examples:
        for x in values:
            pass

        for (x, y) in values:
            pass
    """

    PHRASE_NAME                             = "For Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ForStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'for'
                    "for",

                    # <name>
                    DynamicPhrasesType.Names,

                    # 'in'
                    "in",

                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # ':' <statement>+
                    StatementsPhraseItem.Create(),
                ],
            ),
        )
