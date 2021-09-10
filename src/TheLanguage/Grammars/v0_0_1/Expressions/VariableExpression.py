# ----------------------------------------------------------------------
# |
# |  VariableExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:20:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarPhrase import GrammarPhrase
    from ....Parser.Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem

    from ..Names.TupleName import TupleName


# ----------------------------------------------------------------------
class VariableExpression(GrammarPhrase):
    """\
    A variable name.

    <name>

    Example:
        foo
        bar
        (a, b)
    """

    PHRASE_NAME                             = "Variable Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                # <name>
                PhraseItem(
                    name=self.PHRASE_NAME,
                    item=DynamicPhrasesType.Names,

                    # Ambiguity is introduced between this statement and TupleName without this
                    # explicit exclusion. For example, is "(a, b, c)" a tuple name or tuple
                    # expression? In this context, "tuple expression" is correct, so remove tuple
                    # name as a viable candidate.
                    exclude=[TupleName.PHRASE_NAME],
                ),
            ),
        )
