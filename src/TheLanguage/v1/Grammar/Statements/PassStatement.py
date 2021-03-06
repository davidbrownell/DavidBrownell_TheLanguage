# ----------------------------------------------------------------------
# |
# |  PassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-08 12:40:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PassStatement object"""

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

    from ..Common import Tokens as CommonTokens

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
    )

    from ...Parser.Parser import CreateRegions
    from ...Parser.ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo


# ----------------------------------------------------------------------
class PassStatement(GrammarPhrase):
    """\
    Noop statement.
    """

    PHRASE_NAME                             = "Pass Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PassStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                "pass",
                CommonTokens.Newline,
            ],
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        return PassStatementParserInfo.Create(
            CreateRegions(node),
        )
