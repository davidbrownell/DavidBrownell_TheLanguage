# ----------------------------------------------------------------------
# |
# |  YieldStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:18:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the YieldStatement object"""

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
class YieldStatement(GrammarPhrase):
    """\
    Yields a value to the caller.

    'yield' ('from'? <expr>)?

    Examples:
        yield
        yield foo
        yield from Func()
    """

    PHRASE_NAME                             = "Yield Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(YieldStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "yield",
                    PhraseItem(
                        name="Suffix",
                        item=[
                            PhraseItem(
                                item="from",
                                arity="?",
                            ),
                            DynamicPhrasesType.Expressions,
                        ],
                        arity="?",
                    ),
                    CommonTokens.Newline,
                ],
            ),
        )
