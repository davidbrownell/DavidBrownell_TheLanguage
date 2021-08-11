# ----------------------------------------------------------------------
# |
# |  FuncType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 14:51:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncType object"""

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
class FuncType(GrammarPhrase):
    """\
    A first-class function type.

    '(' <type> '(' (<type> (',' <type>)* ','?)? ')' ')'

    Examples:
        (Int ())
        (Int (Char, Bool))
    """

    NODE_NAME                               = "Func Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncType, self).__init__(
            GrammarPhrase.Type.Type,
            CreatePhrase(
                name=self.NODE_NAME,
                item=[
                    # '(' (outer)
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <type> (return)
                    DynamicPhrasesType.Types,

                    # '(' (inner)
                    "(",

                    PhraseItem(
                        name="Parameters",
                        item=[
                            # <type> (parameter)
                            DynamicPhrasesType.Types,

                            # (',' <type>)*
                            PhraseItem(
                                name="Comma and Type",
                                item=[
                                    ",",
                                    DynamicPhrasesType.Types,
                                ],
                                arity="*",
                            ),

                            # ',' (trailing parameter)
                            PhraseItem(
                                item=",",
                                arity="?",
                            ),
                        ],
                        arity="?",
                    ),

                    # ')' (inner)
                    ")",

                    # ')' (outer)
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",
                ],
            ),
        )
