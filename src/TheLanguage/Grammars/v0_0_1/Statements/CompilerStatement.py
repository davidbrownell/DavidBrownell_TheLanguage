# ----------------------------------------------------------------------
# |
# |  CompilerStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-03 09:54:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CompilerStatement object"""

import os

from typing import Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Impl.MultilineStatementBase import MultilineStatementBase
    from ...GrammarPhrase import GrammarPhrase
    from ....Lexer.LexerInfo import SetLexerInfo
    from ....Parser.Phrases.DSL import Leaf, Node


# ----------------------------------------------------------------------
class CompilerStatement(MultilineStatementBase):
    """\
    A statement that contains instructions used during the complication process.

    '<<<!!!'
    <content>
    '!!!>>>'
    """

    PHRASE_NAME                             = "Compiler Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(CompilerStatement, self).__init__(
            self.PHRASE_NAME,
            "<<<!!!",
            "!!!>>>",
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _ValidateSyntaxImpl(
        self,
        node: Node,
        leaf: Leaf,
        value: str,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # Persist the info
        pass # TODO

        SetLexerInfo(node, None)
