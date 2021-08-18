# ----------------------------------------------------------------------
# |
# |  BinaryStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-17 13:07:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryStatement object"""

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
class BinaryStatement(GrammarPhrase):
    """\
    Statement that follows the form:

    <name> <op> <expr>

    Examples:
        value += one
        value <<= two
    """

    PHRASE_NAME                             = "Binary Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BinaryStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <name>
                    DynamicPhrasesType.Names,

                    # <op>
                    CreatePhrase(
                        name="Operator",
                        item=(
                            # Mathematical
                            "+=",           # Addition
                            "-=",           # Subtraction
                            "*=",           # Multiplication
                            "**=",          # Power
                            "/=",           # Decimal Division
                            "//=",          # Integer Division
                            "%=",           # Modulo

                            # Bit Manipulation
                            "<<=",          # Left Shift
                            ">>=",          # Right Shift
                            "^=",           # Xor
                            "|=",           # Bitwise or
                            "&=",           # Bitwise and
                        ),
                    ),

                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # End
                    CommonTokens.Newline,
                ],
            ),
        )
