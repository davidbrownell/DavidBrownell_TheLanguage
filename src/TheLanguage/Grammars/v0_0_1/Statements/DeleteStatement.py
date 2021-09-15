# ----------------------------------------------------------------------
# |
# |  DeleteStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 16:44:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DeleteStatement object"""

import os

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo

    from ....Lexer.Statements.DeleteStatementLexerInfo import (
        DeleteStatementLexerData,
        DeleteStatementLexerInfo,
        DeleteStatementLexerRegions,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
class DeleteStatement(GrammarPhrase):
    """\
    Deletes a variable so that it is no longer accessible.

    'del' <name>

    Examples:
        del foo
        del bar
    """

    PHRASE_NAME                             = "Delete Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(DeleteStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "del",
                    CommonTokens.GenericName,
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <name>
            name_leaf = cast(Leaf, nodes[1])
            name_data = cast(str, ExtractToken(name_leaf))

            SetLexerInfo(
                node,
                DeleteStatementLexerInfo(
                    DeleteStatementLexerData(name_data),
                    CreateLexerRegions(
                        DeleteStatementLexerRegions,  # type: ignore
                        node,
                        name_leaf,
                    ),
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
