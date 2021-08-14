# ----------------------------------------------------------------------
# |
# |  TransferExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 15:30:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TransferExpression object"""

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
class TransferExpression(GrammarPhrase):
    """\
    Transfers a variable.

    'move'|'copy' <name>

    Example:
        move foo
        copy (bar, baz)
    """

    NODE_NAME                               = "Transfer Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TransferExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.NODE_NAME,

                item=[
                    # 'move' | 'copy'
                    ("move", "copy"),

                    # <name>
                    DynamicPhrasesType.Names,
                ],
            ),
        )
