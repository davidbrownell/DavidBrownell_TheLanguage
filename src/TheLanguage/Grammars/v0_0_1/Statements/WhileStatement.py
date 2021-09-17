# ----------------------------------------------------------------------
# |
# |  WhileStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 16:17:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the WhileStatement object"""

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
    from ..Common import StatementsPhraseItem
    from ...GrammarPhrase import CreateParserRegions, GrammarPhrase

    from ....Parser.ParserInfo import GetParserInfo, SetParserInfo
    from ....Parser.Statements.WhileStatementParserInfo import (
        ExpressionParserInfo,
        WhileStatementParserInfo,
    )

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
        Node,
    )


# ----------------------------------------------------------------------
class WhileStatement(GrammarPhrase):
    """\
    Executes statements while a condition is true.

    'while' <expr> ':'
        <statement>+

    Examples:
        while Func1():
            pass

        while one and two:
            pass
    """

    PHRASE_NAME                             = "While Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(WhileStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'while'
                    "while",

                    # <expr>
                    DynamicPhrasesType.Expressions,

                    StatementsPhraseItem.Create(),
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

            # <expr>
            expr_node = cast(Node, ExtractDynamic(cast(Node, nodes[1])))
            expr_info = cast(ExpressionParserInfo, GetParserInfo(expr_node))

            # <statements>
            statements_node = cast(Node, nodes[2])
            statements_info = StatementsPhraseItem.ExtractParserInfo(statements_node)

            SetParserInfo(
                node,
                WhileStatementParserInfo(
                    CreateParserRegions(node, expr_node, statements_node),  # type: ignore
                    expr_info,
                    statements_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
