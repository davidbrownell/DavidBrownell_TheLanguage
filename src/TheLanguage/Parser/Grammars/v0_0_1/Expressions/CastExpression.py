# ----------------------------------------------------------------------
# |
# |  CastExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 11:25:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CastExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.TypeModifier import TypeModifier
    from ...GrammarPhrase import GrammarPhrase
    from ....Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
class CastExpression(GrammarPhrase):
    """\
    Casts a variable to a different type.

    <expr> 'as' <modifier> | <type>

    Examples:
        foo = bar as Int
        biz = baz as Int val
        another = a_var as val
    """

    PHRASE_NAME                             = "Cast Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(CastExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # 'as'
                    "as",

                    # <modifier> | <type>
                    PhraseItem(
                        name="Type or Modifier",
                        item=(
                            TypeModifier.CreatePhraseItem(),
                            DynamicPhrasesType.Types,
                        ),
                    ),
                ],
                is_left_recursive_sequence=True,
            ),
        )
