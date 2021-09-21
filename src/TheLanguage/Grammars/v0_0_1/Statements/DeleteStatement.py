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
    from ...GrammarPhrase import CreateParserRegions, GrammarPhrase

    from ....Parser.ParserInfo import GetParserInfo, SetParserInfo

    from ....Parser.Statements.DeleteStatementParserInfo import DeleteStatementParserInfo

    from ....Lexer.Phrases.DSL import (
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
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        # ----------------------------------------------------------------------
        def CreateParserInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <name>
            name_leaf = cast(Leaf, nodes[1])
            name_info = cast(str, ExtractToken(name_leaf))

            SetParserInfo(
                node,
                DeleteStatementParserInfo(
                    CreateParserRegions(node, name_leaf),  # type: ignore
                    name_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
