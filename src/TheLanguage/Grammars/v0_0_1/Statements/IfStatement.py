# ----------------------------------------------------------------------
# |
# |  IfStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-28 21:45:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IfStatement object"""

import os

from typing import cast, List, Optional, Union

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
    from ....Parser.Statements.IfStatementParserInfo import (
        ExpressionParserInfo,
        IfStatementClauseParserInfo,
        IfStatementParserInfo,
    )

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class IfStatement(GrammarPhrase):
    """\
    If/Else If/Else statement.

    'if <expr> ':'
        <statement>+
    (
        'elif' <expr> ':'
            <statement>+
    )*
    (
        'else' ':'
            <statement>+
    )?

    Examples:
        if cond1:
            Func1()
        elif cond2:
            Func2()
            Func3()
        elif cond3:
            Func4()
        else:
            Func5()
            Func6()
    """

    PHRASE_NAME                             = "If Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        statements_item = StatementsPhraseItem.Create()

        super(IfStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'if' <expr> ':'
                    #     <statement>+
                    "if",
                    DynamicPhrasesType.Expressions,
                    statements_item,

                    # (
                    #     'elif' <expr> ':'
                    #          <statement>+
                    # )*
                    PhraseItem(
                        name="Elif",
                        item=[
                            "elif",
                            DynamicPhrasesType.Expressions,
                            statements_item,
                        ],
                        arity="*",
                    ),

                    # (
                    #     'else' ':'
                    #         <statement>+
                    # )?
                    PhraseItem(
                        name="Else",
                        item=[
                            "else",
                            statements_item,
                        ],
                        arity="?",
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        # ----------------------------------------------------------------------
        def CreateParserInfo():
            nodes = cast(List[Node], ExtractSequence(node))
            assert len(nodes) == 5

            clauses: List[IfStatementClauseParserInfo] = []

            # 'if'...
            clauses.append(cls._CreateIfStatementClause(nodes))

            # 'elif'...
            for else_node in cast(List[Node], ExtractRepeat(cast(Node, nodes[3]))):
                clauses.append(cls._CreateIfStatementClause(else_node))

            # 'else'...
            else_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[4])))
            if else_node is not None:
                else_nodes = ExtractSequence(else_node)
                assert len(else_nodes) == 2

                else_info = StatementsPhraseItem.ExtractParserInfo(cast(Node, else_nodes[1]))
            else:
                else_info = None

            assert clauses

            SetParserInfo(
                node,
                IfStatementParserInfo(
                    CreateParserRegions(node, node, else_node),  # type: ignore
                    clauses,
                    else_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateIfStatementClause(
        node_or_nodes: Union[Node, List[Node]],
    ) -> IfStatementClauseParserInfo:
        if isinstance(node_or_nodes, Node):
            nodes = ExtractSequence(node_or_nodes)
            containing_node = node_or_nodes

        elif isinstance(node_or_nodes, list):
            nodes = node_or_nodes
            containing_node = nodes[0].Parent
            assert containing_node is not None

        else:
            assert False, node_or_nodes

        assert len(nodes) >= 3

        cond_node = cast(Node, ExtractDynamic(cast(Node, nodes[1])))
        cond_info = cast(ExpressionParserInfo, GetParserInfo(cond_node))

        statements_node = cast(Node, nodes[2])
        statements_info = StatementsPhraseItem.ExtractParserInfo(statements_node)

        # pylint: disable=too-many-function-args
        return IfStatementClauseParserInfo(
            CreateParserRegions(containing_node, cond_node, statements_node),  # type: ignore
            cond_info,
            statements_info,
        )
