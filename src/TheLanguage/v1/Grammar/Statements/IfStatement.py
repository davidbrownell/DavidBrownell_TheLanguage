# ----------------------------------------------------------------------
# |
# |  IfStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-21 14:43:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IfStatement object"""

import itertools
import os

from typing import cast, List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import StatementsFragment

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        OptionalPhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ...Parser.Parser import CreateRegions, GetParserInfo

    from ...Parser.ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...Parser.ParserInfos.Statements.IfStatementParserInfo import (
        IfStatementClauseParserInfo,
        IfStatementParserInfo,
    )


# ----------------------------------------------------------------------
class IfStatement(GrammarPhrase):
    PHRASE_NAME                             = "If Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        statements_item = StatementsFragment.Create()

        super(IfStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                # 'if' <expression> <statements>
                "if",
                DynamicPhrasesType.Expressions,
                statements_item,

                # ('elif' <expression> <statements>)*
                ZeroOrMorePhraseItem(
                    name="Elif",
                    item=[
                        "elif",
                        DynamicPhrasesType.Expressions,
                        statements_item,
                    ],
                ),

                # ('else' <statements>)?
                OptionalPhraseItem(
                    name="Else",
                    item=[
                        "else",
                        statements_item,
                    ],
                ),
            ],
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            clauses: List[IfStatementClauseParserInfo] = []

            for clause_node in itertools.chain(
                [node],
                (
                    clause_node
                    for clause_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, nodes[3])))
                )
            ):
                clause_nodes = ExtractSequence(clause_node)
                assert len(clause_nodes) >= 3

                # <expression>
                expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, clause_nodes[1])))
                expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

                # <statements>
                statements_node = cast(AST.Node, clause_nodes[2])
                statements_info, docstring_info = StatementsFragment.Extract(statements_node)

                if docstring_info is None:
                    docstring_node = None
                else:
                    docstring_node, docstring_info = docstring_info

                clauses.append(
                    IfStatementClauseParserInfo.Create(
                        CreateRegions(clause_node, statements_node, docstring_node),
                        expression_info,
                        statements_info,
                        docstring_info,
                    ),
                )

            # ('else' <statements>)?
            else_statements_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[4])))
            if else_statements_node is None:
                else_statements_info = None
                else_docstring_node = None
                else_docstring_info = None

            else:
                else_statements_nodes = ExtractSequence(else_statements_node)
                assert len(else_statements_nodes) == 2

                else_statements_node = cast(AST.Node, else_statements_nodes[1])
                else_statements_info, else_docstring_info = StatementsFragment.Extract(else_statements_node)

                if else_docstring_info is None:
                    else_docstring_node = None
                else:
                    else_docstring_node, else_docstring_info = else_docstring_info

            return IfStatementParserInfo.Create(
                CreateRegions(node, else_statements_node, else_docstring_node),
                clauses,
                else_statements_info,
                else_docstring_info,
            )

        # ----------------------------------------------------------------------

        return Callback
