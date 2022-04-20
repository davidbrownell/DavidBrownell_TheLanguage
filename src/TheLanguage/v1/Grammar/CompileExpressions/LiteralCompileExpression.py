# ----------------------------------------------------------------------
# |
# |  LiteralCompileExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-18 13:51:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LiteralCompileExpression object"""

import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import LiteralFragment

    from ...Lexer.Phrases.DSL import CreatePhrase, DynamicPhrasesType


# ----------------------------------------------------------------------
class LiteralCompileExpression(GrammarPhrase):
    PHRASE_NAME                             = "Literal CompileExpression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(LiteralCompileExpression, self).__init__(
            DynamicPhrasesType.CompileExpressions,
            CreatePhrase(LiteralFragment.Create(self.PHRASE_NAME)),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        return LiteralFragment.Extract(node)
