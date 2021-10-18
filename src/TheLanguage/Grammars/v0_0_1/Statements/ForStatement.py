# ----------------------------------------------------------------------
# |
# |  ForStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 14:48:25
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

    from ....Parser.Statements.IterateStatementParserInfo import (
        ExpressionParserInfo,
        IterateStatementParserInfo,
        NameParserInfo,
    )


# ----------------------------------------------------------------------
class ForStatement(GrammarPhrase):
    """\
    Statement that exercises as interator.

    'for' <name> 'in' <expression> ':'
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
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'for'
                    "for",

                    # <name>
                    DynamicPhrasesType.Names,

                    # 'in'
                    "in",

                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # ":" <statement>+
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
            assert len(nodes) == 5

            # <name>
            name_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
            name_info = cast(NameParserInfo, GetParserInfo(name_node))

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[3])))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # <statement>+
            statement_node = cast(AST.Node, nodes[4])
            statement_info = StatementsPhraseItem.ExtractParserInfo(statement_node)

            return IterateStatementParserInfo(
                CreateParserRegions(node, name_node, expression_node, statement_node),  # type: ignore
                name_info,
                expression_info,
                statement_info,
            )

        # ----------------------------------------------------------------------

        return Impl
