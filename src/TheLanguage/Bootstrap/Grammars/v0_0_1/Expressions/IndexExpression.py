# ----------------------------------------------------------------------
# |
# |  IndexExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-07 11:40:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IndexExpression object"""

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
        ExtractDynamic,
        ExtractSequence,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Expressions.IndexExpressionParserInfo import (
        ExpressionParserInfo,
        IndexExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class IndexExpression(GrammarPhrase):
    """\
    Applies an index operation to an expression.

    <expression> '[' <expression> ']'

    Examples:
        foo[1]
        bar[(1, 2)]
        baz[a][b][c]
    """

    PHRASE_NAME                             = "Index Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(IndexExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # '['
                    "[",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # ']'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    "]",
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
            assert len(nodes) == 6

            # <expression> (prefix)
            expression_node = ExtractDynamic(cast(AST.Node, nodes[0]))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # <expression> (index)
            index_node = ExtractDynamic(cast(AST.Node, nodes[3]))
            index_info = cast(ExpressionParserInfo, GetParserInfo(index_node))

            return IndexExpressionParserInfo(
                CreateParserRegions(node, expression_node, index_node),  # type: ignore
                expression_info,
                index_info,
            )

        # ----------------------------------------------------------------------

        return Impl
