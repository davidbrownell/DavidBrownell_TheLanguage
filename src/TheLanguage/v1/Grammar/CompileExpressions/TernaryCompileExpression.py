# ----------------------------------------------------------------------
# |
# |  TernaryCompileExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 15:34:46
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryCompileExpression object"""

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
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
    )

    from ...Parser.Parser import CreateRegions, GetParserInfo

    from ...Parser.ParserInfos.CompileExpressions.TernaryCompileExpressionParserInfo import (
        CompileExpressionParserInfo,
        TernaryCompileExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class TernaryCompileExpression(GrammarPhrase):
    PHRASE_NAME                             = "Ternary CompileExpression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TernaryCompileExpression, self).__init__(
            DynamicPhrasesType.CompileExpressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <true_expression>
                    DynamicPhrasesType.CompileExpressions,
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # 'if'
                    "if",

                    # <condition_expression>
                    DynamicPhrasesType.CompileExpressions,

                    # 'else'
                    "else",

                    # <false_expression>
                    CommonTokens.PopIgnoreWhitespaceControl,
                    DynamicPhrasesType.CompileExpressions,
                ],
            ),
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
            assert len(nodes) == 7

            # <true_expression>
            true_expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            true_expression_info = cast(CompileExpressionParserInfo, GetParserInfo(true_expression_node))

            # <condition_expression>
            condition_expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[3])))
            condition_expression_info = cast(CompileExpressionParserInfo, GetParserInfo(condition_expression_node))

            # <false_expression>
            false_expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[6])))
            false_expression_info = cast(CompileExpressionParserInfo, GetParserInfo(false_expression_node))

            return TernaryCompileExpressionParserInfo.Create(
                CreateRegions(node),
                condition_expression_info,
                true_expression_info,
                false_expression_info,
            )

        # ----------------------------------------------------------------------

        return Callback
