# ----------------------------------------------------------------------
# |
# |  TernaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 19:28:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarPhrase import GrammarPhrase
    from ....Phrases.DSL import CreatePhrase, DynamicPhrasesType


# ----------------------------------------------------------------------
class TernaryExpression(GrammarPhrase):
    """\
    Expression that yields on value on True and a different value on False.

    <expr> 'if' <expr> 'else' <expr>

    Examples:
        "The Truth" if SomeExpr() else "The Lie"
    """

    NODE_NAME                               = "Ternary Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TernaryExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.NODE_NAME,
                item=[
                    DynamicPhrasesType.Expressions,
                    "if",
                    DynamicPhrasesType.Expressions,
                    "else",
                    DynamicPhrasesType.Expressions,
                ],
                suffers_from_infinite_recursion=True,
            ),
        )
