# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:25:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableDeclarationStatement object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ..Common.TypeModifier import TypeModifier
    from ...GrammarPhrase import GrammarPhrase
    from ....Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class VariableDeclarationStatement(GrammarPhrase):
    """\
    Declares a variable.

    <modifier>? <name> '=' <expr>

    Examples:
        foo = bar
        (a, b,) = Func()
    """

    NODE_NAME                               = "Variable Declaration Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableDeclarationStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.NODE_NAME,
                item=[
                    # <modifier>?
                    PhraseItem(
                        name="Modifier",
                        item=TypeModifier.CreatePhraseItem(),
                        arity="?",
                    ),

                    # <name>
                    DynamicPhrasesType.Names,

                    "=",

                    # <expr>
                    DynamicPhrasesType.Expressions,
                    CommonTokens.Newline,
                ],
            ),
        )
