# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 14:34:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

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
class VariantType(GrammarPhrase):
    """\
    A type that can be any one of a collection of types.

    '(' <type> '|' (<type> '|')+ <type> ')'

    Examples:
        (Int | Float)
        (Int val | Bool | Char view)
    """

    NODE_NAME                               = "Variant Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariantType, self).__init__(
            GrammarPhrase.Type.Type,
            CreatePhrase(
                name=self.NODE_NAME,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <type>
                    DynamicPhrasesType.Types,

                    # (<type> '|')+
                    PhraseItem(
                        name="Type and Sep",
                        item=[
                            DynamicPhrasesType.Types,
                            "|",
                        ],
                        arity="+",
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # ")"
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",
                ],
            ),
        )
