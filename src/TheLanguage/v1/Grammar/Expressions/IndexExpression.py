# ----------------------------------------------------------------------
# |
# |  IndexExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-01 14:54:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IndexExpression object"""

import os

from typing import cast

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, GrammarPhrase

    from ..Common import Tokens as CommonTokens

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
    )

    from ...Parser.Parser import CreateRegions, GetParserInfo

    from ...Parser.ParserInfos.Expressions.IndexExpressionParserInfo import (
        ExpressionParserInfo,
        IndexExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class IndexExpression(GrammarPhrase):
    PHRASE_NAME                             = "Index Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(IndexExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # <lhs_expression>
                DynamicPhrasesType.Expressions,

                # '['
                "[",
                CommonTokens.PushIgnoreWhitespaceControl,

                # <index_expression>
                DynamicPhrasesType.Expressions,

                # ']'
                CommonTokens.PopIgnoreWhitespaceControl,
                "]",
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
            assert len(nodes) == 6

            # <lhs_expression>
            lhs_expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            lhs_expression_info = cast(ExpressionParserInfo, GetParserInfo(lhs_expression_node))

            # <index_expression>
            index_expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[3])))
            index_expression_info = cast(ExpressionParserInfo, GetParserInfo(index_expression_node))

            return IndexExpressionParserInfo.Create(
                CreateRegions(node),
                lhs_expression_info,
                index_expression_info,
            )

        # ----------------------------------------------------------------------

        return Callback
