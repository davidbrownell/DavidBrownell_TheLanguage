# ----------------------------------------------------------------------
# |
# |  BinaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 15:42:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryExpression object"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarPhrase import GrammarPhrase
    from ....Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
class BinaryExpression(GrammarPhrase):
    """\
    Expression that follows the form:

    <expr> <op> <expr>

    Example:
        one + two
        foo / bar
        biz and baz
    """

    PHRASE_NAME                             = "Binary Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BinaryExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # <op>
                    CreatePhrase(
                        name="Operator",
                        item=(
                            # Logical
                            "and",          # Logical and
                            "or",           # Logical or
                            "in",           # Collection membership
                            "is",           # Object identity

                            # Comparison
                            "<",            # Less than
                            "<=",           # Less than or equal to
                            ">",            # Greater than
                            ">=",           # Greater than or equal to
                            "==",           # Equals
                            "!=",           # Not equals

                            # Mathematical
                            "+",            # Addition
                            "-",            # Subtraction
                            "*",            # Multiplication
                            "**",           # Power
                            "/",            # Decimal division
                            "//",           # Integer division
                            "%",            # Modulo

                            # Bit Manipulation
                            "<<",           # Left shift
                            ">>",           # Right shift
                            "^",            # Xor
                            "|",            # Bitwise or
                            "&",            # Bitwise and
                        ),
                    ),

                    # <expr>
                    DynamicPhrasesType.Expressions,
                ],
                suffers_from_infinite_recursion=True,
            ),
        )
