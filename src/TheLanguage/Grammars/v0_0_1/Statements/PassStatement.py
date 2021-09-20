# ----------------------------------------------------------------------
# |
# |  PassStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 22:49:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PassStatement"""

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
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import CreateParserRegions, GrammarPhrase

    from ....Parser.ParserInfo import SetParserInfo
    from ....Parser.Statements.PassStatementParserInfo import PassStatementParserInfo

    from ....Lexer.Phrases.DSL import CreatePhrase, Node


# ----------------------------------------------------------------------
class PassStatement(GrammarPhrase):
    """\
    Noop statement.

    'pass'

    Example:
        Int var Func():
            pass
    """

    PHRASE_NAME                             = "Pass Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(PassStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "pass",
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        SetParserInfo(
            node,
            PassStatementParserInfo(
                CreateParserRegions(node),  # type: ignore
            ),
        )
