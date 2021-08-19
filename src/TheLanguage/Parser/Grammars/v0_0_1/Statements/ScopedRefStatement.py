# ----------------------------------------------------------------------
# |
# |  ScopedRefStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 15:45:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ScopedRefStatement object"""

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
    from ....Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
class ScopedRefStatement(GrammarPhrase):
    """\
    Acquires the reference of a variable while the scope is active.

    'with' (<refs_expression>| '(' <refs_expression> ')') ':'
        <statement>+

    Examples:
        with var1 as ref:
            pass

        with var1 as ref, var2 as ref:
            pass

        with (
            var1 as ref,
            var2 as ref,
            var3 as ref,
        ):
            pass
    """

    PHRASE_NAME                             = "Scoped Ref Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        refs_expression = PhraseItem(
            name="Refs",
            item=[
                # <ref_expression>
                DynamicPhrasesType.Names,

                PhraseItem(
                    name="Comma and Ref",
                    item=[
                        ",",
                        DynamicPhrasesType.Names,
                    ],
                    arity="*",
                ),

                PhraseItem(
                    name="Trailing Comma",
                    item=",",
                    arity="?",
                ),
            ],
        )

        super(ScopedRefStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'with'
                    "with",

                    # Refs
                    (
                        # '(' <refs_expression> ')'
                        PhraseItem(
                            name="Grouped",
                            item=[
                                # '('
                                "(",
                                CommonTokens.PushIgnoreWhitespaceControl,

                                # <refs_expression>
                                refs_expression,

                                # ')'
                                CommonTokens.PopIgnoreWhitespaceControl,
                                ")",
                            ],
                        ),

                        # <refs_expression>
                        refs_expression,
                    ),

                    # 'as'
                    "as",

                    # 'ref'
                    TypeModifier.ref.name,

                    # ':"
                    ":",
                    CommonTokens.Newline,
                    CommonTokens.Indent,

                    # <statement>+
                    PhraseItem(
                        name="Statements",
                        item=DynamicPhrasesType.Statements,
                        arity="+",
                    ),

                    # End
                    CommonTokens.Dedent,
                ],
            ),
        )
