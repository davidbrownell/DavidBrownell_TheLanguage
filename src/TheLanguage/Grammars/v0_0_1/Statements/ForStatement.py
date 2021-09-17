# ----------------------------------------------------------------------
# |
# |  ForStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-17 22:39:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ForStatement object"""

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
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo
    from ....Lexer.Statements.ForStatementLexerInfo import (
        ExpressionLexerInfo,
        ForStatementLexerInfo,
        NameLexerInfo,
    )

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
        Node,
    )


# ----------------------------------------------------------------------
class ForStatement(GrammarPhrase):
    """\
    Statement that exercises an iterator.

    'for' <name> 'in' <expr> ':'
        <statement>+

    Examples:
        for x in values:
            pass

        for (x, y) in values:
            pass
    """

    PHRASE_NAME                             = "For Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ForStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'for'
                    "for",

                    # <name>
                    DynamicPhrasesType.Names,

                    # 'in'
                    "in",

                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # ':' <statement>+
                    StatementsPhraseItem.Create(),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractLexerInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            # <name>
            name_node = cast(Node, ExtractDynamic(cast(Node, nodes[1])))
            name_info = cast(NameLexerInfo, GetLexerInfo(name_node))

            # <expr>
            expr_node = cast(Node, ExtractDynamic(cast(Node, nodes[3])))
            expr_info = cast(ExpressionLexerInfo, GetLexerInfo(expr_node))

            # <statements>
            statement_node = cast(Node, nodes[4])
            statement_info = StatementsPhraseItem.ExtractLexerInfo(statement_node)

            SetLexerInfo(
                node,
                ForStatementLexerInfo(
                    CreateLexerRegions(node, name_node, expr_node, statement_node),  # type: ignore
                    name_info,
                    expr_info,
                    statement_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
