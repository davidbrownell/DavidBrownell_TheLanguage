# ----------------------------------------------------------------------
# |
# |  DeleteStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 14:25:08
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

from typing import Callable, cast, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
    )

    from ....Parser.Parser import CreateParserRegions

    from ....Parser.Statements.DeleteStatementParserInfo import DeleteStatementParserInfo


# ----------------------------------------------------------------------
# TODO: Should support deleting a list of items
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
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "del",
                    CommonTokens.VariableName,
                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        # <name>
        name_leaf = cast(AST.Leaf, nodes[1])
        name_info = cast(str, ExtractToken(name_leaf))

        return DeleteStatementParserInfo(
            CreateParserRegions(node, name_leaf),  # type: ignore
            name_info,
        )
