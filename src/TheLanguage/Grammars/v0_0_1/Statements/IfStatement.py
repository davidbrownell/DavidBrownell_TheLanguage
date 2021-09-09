# ----------------------------------------------------------------------
# |
# |  IfStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-28 21:45:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IfStatement object"""

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
    from ....Parser.Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
class IfStatement(GrammarPhrase):
    """\
    If/Else If/Else statement.

    'if <expr> ':'
        <statement>+
    (
        'elif' <expr> ':'
            <statement>+
    )*
    (
        'else' ':'
            <statement>+
    )?

    Examples:
        if cond1:
            Func1()
        elif cond2:
            Func2()
            Func3()
        elif cond3:
            Func4()
        else:
            Func5()
            Func6()
    """

    PHRASE_NAME                             = "If Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        statements_item = StatementsPhraseItem.Create()

        super(IfStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'if' <expr> ':'
                    #     <statement>+
                    "if",
                    DynamicPhrasesType.Expressions,
                    statements_item,

                    # (
                    #     'elif' <expr> ':'
                    #          <statement>+
                    # )*
                    PhraseItem(
                        name="Elif",
                        item=[
                            "elif",
                            DynamicPhrasesType.Expressions,
                            statements_item,
                        ],
                        arity="*",
                    ),

                    # (
                    #     'else' ':'
                    #         <statement>+
                    # )?
                    PhraseItem(
                        name="Else",
                        item=[
                            "else",
                            statements_item,
                        ],
                        arity="?",
                    ),
                ],
            ),
        )
