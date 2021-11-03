# ----------------------------------------------------------------------
# |
# |  IfStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 16:20:13
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

from typing import Callable, cast, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import StatementsPhraseItem

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        OptionalPhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.IfStatementParserInfo import (
        ExpressionParserInfo,
        IfStatementClauseParserInfo,
        IfStatementParserInfo,
    )


# ----------------------------------------------------------------------
class IfStatement(GrammarPhrase):
    """\
    If/Else If/Else statement,

    'if' <expression> ':'
        <statement>+
    (
        'elif' <expression> ':'
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
        else:
            Func4()
    """

    PHRASE_NAME                             = "If Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        statements_item = StatementsPhraseItem.Create()

        super(IfStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'if' <expression> ':'
                    #     <statement>+
                    "if",
                    DynamicPhrasesType.Expressions,
                    statements_item,

                    # (
                    #     'elif' <expression> ':'
                    #         <statement>+
                    # )*
                    ZeroOrMorePhraseItem.Create(
                        name="Elif",
                        item=[
                            "elif",
                            DynamicPhrasesType.Expressions,
                            statements_item,
                        ],
                    ),

                    # (
                    #     'else' ':'
                    #         <statement>+
                    # )?
                    OptionalPhraseItem.Create(
                        name="Else",
                        item=[
                            "else",
                            statements_item,
                        ],
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            clause_infos: List[IfStatementClauseParserInfo] = []

            # 'if'...
            clause_infos.append(cls._CreateIfStatementClause(cast(List[AST.Node], nodes)))

            # 'elif'...
            for elif_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, nodes[3]))):
                clause_infos.append(cls._CreateIfStatementClause(elif_node))

            # 'else'...
            else_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[4])))
            if else_node is None:
                else_info = None
            else:
                else_nodes = ExtractSequence(else_node)
                assert len(else_nodes) == 2

                else_info = StatementsPhraseItem.ExtractParserInfo(cast(AST.Node, else_nodes[1]))

            assert clause_infos

            return IfStatementParserInfo(
                CreateParserRegions(node, else_node),  # type: ignore
                clause_infos,
                else_info,
            )

        # ----------------------------------------------------------------------

        return Impl

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateIfStatementClause(
        node_or_nodes: Union[AST.Node, List[AST.Node]],
    ) -> IfStatementClauseParserInfo:
        if isinstance(node_or_nodes, AST.Node):
            nodes = ExtractSequence(node_or_nodes)
            containing_node = node_or_nodes

        elif isinstance(node_or_nodes, list):
            nodes = node_or_nodes
            containing_node = nodes[0].Parent

        else:
            assert False, node_or_nodes  # pragma: no cover

        assert len(nodes) >= 3

        # <condition>
        condition_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
        condition_info = cast(ExpressionParserInfo, GetParserInfo(condition_node))

        # <statement>+
        statements_node = cast(AST.Node, nodes[2])
        statements_info = StatementsPhraseItem.ExtractParserInfo(statements_node)

        # pylint: disable=too-many-function-args
        return IfStatementClauseParserInfo(
            CreateParserRegions(containing_node, condition_node, statements_node),  # type: ignore
            condition_info,
            statements_info,
        )
