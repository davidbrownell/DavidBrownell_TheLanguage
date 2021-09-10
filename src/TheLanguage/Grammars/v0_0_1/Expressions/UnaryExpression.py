# ----------------------------------------------------------------------
# |
# |  UnaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 11:43:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryExpression object"""

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
class UnaryExpression(GrammarPhrase):
    """\
    A prefix to an expression.

    <op> <expr>

    Example:
        not foo
        -bar
    """

    PHRASE_NAME                             = "Unary Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(UnaryExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <op>
                    PhraseItem(
                        name="Operator",
                        item=tuple(
                            # Note that any alphanumeric operators added here must also be added to
                            # `DoNotMatchKeywords` in ../Common/Tokens.py.
                            [
                                # Coroutine
                                "await",

                                # Transfer
                                "copy",
                                "move",

                                # Logical
                                "not",

                                # Mathematical
                                "+",
                                "-",

                                # Bit Manipulation
                                "~",        # Bit Complement
                            ],
                        ),
                    ),

                    # <expr>
                    DynamicPhrasesType.Expressions,
                ],
            ),
        )
