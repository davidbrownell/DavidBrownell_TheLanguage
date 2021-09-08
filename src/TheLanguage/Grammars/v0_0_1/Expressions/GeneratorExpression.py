# ----------------------------------------------------------------------
# |
# |  GeneratorExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 19:13:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GeneratorExpression object"""

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

    from .TernaryExpression import TernaryExpression


# ----------------------------------------------------------------------
class GeneratorExpression(GrammarPhrase):
    """\
    Expression that generates values.

    <expr> 'for' <name> 'in' <expr> ('if' <expr>)?

    Examples:
        AddOne(value) for value in OneToTen()
        AddOne(value) for value in OneToTen() if value % 2 == 0
    """

    PHRASE_NAME                             = "Generator Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GeneratorExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # 'for'
                    "for",

                    # <name>
                    DynamicPhrasesType.Names,

                    # 'in'
                    "in",

                    # <expr>
                    PhraseItem(
                        item=DynamicPhrasesType.Expressions,

                        # Don't let the TernaryExpression capture the 'if' token that may follow, as
                        # the TernaryExpression expects an 'else' clause, but the following 'if' will
                        # never have one.
                        exclude=[TernaryExpression.PHRASE_NAME],
                    ),

                    # ('if' <expr>)?
                    PhraseItem(
                        name="Conditional",
                        item=[
                            # 'if'
                            "if",

                            # <expr>
                            DynamicPhrasesType.Expressions,
                        ],
                        arity="?",
                    ),
                ],
            ),
        )