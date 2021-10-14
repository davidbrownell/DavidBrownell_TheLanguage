# ----------------------------------------------------------------------
# |
# |  WhileStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 12:09:45
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

from typing import Callable, cast, Tuple, Union

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
        ExtractSequence,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.WhileStatementParserInfo import (
        ExpressionParserInfo,
        WhileStatementParserInfo,
    )


# ----------------------------------------------------------------------
class WhileStatement(GrammarPhrase):
    """\
    Executes statements while a condition is true.

    'while' <expression> ':'
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
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'while'
                    "while",

                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # ':' <statement>+
                    StatementsPhraseItem.Create(),
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
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # <statement>+
            statements_node = cast(AST.Node, nodes[2])
            statements_info = StatementsPhraseItem.ExtractParserInfo(statements_node)

            return WhileStatementParserInfo(
                CreateParserRegions(node, expression_node, statements_node),  # type: ignore
                expression_info,
                statements_info,
            )

        # ----------------------------------------------------------------------

        return Impl
