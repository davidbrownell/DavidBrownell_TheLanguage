# ----------------------------------------------------------------------
# |
# |  UnaryCompileExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 14:11:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryCompileExpression object"""

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

    from ...Parser.ParserInfos.CompileExpressions.UnaryCompileExpressionParserInfo import (
        CompileExpressionParserInfo,
        OperatorType,
        UnaryCompileExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class UnaryCompileExpression(GrammarPhrase):
    PHRASE_NAME                             = "Unary CompileExpression"

    # TODO: Precedence
    OPERATOR_MAP                            = {
        "+": OperatorType.Positive,
        "-": OperatorType.Negative,

        "not": OperatorType.Not,
    }

    assert len(OPERATOR_MAP) == len(OperatorType)

    # ----------------------------------------------------------------------
    def __init__(self):
        super(UnaryCompileExpression, self).__init__(
            DynamicPhrasesType.CompileExpressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <operator>
                    PhraseItem(
                        name="Operator",
                        item=tuple(self.__class__.OPERATOR_MAP.keys()),
                    ),

                    # <expression>
                    DynamicPhrasesType.CompileExpressions,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: AST.Node,
    ) -> GrammarPhrase.ExtractParserInfoReturnType:
        # ----------------------------------------------------------------------
        def Callback():
            nodes = ExtractSequence(node)
            assert len(nodes) == 2

            # <operator>
            operator_node = cast(AST.Leaf, ExtractOr(cast(AST.Node, nodes[0])))
            operator_info = ExtractToken(
                operator_node,
                return_match_contents=True,
            )

            operator_info = cls.OPERATOR_MAP[operator_info]

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[1])))
            expression_info = cast(CompileExpressionParserInfo, GetParserInfo(expression_node))

            return UnaryCompileExpressionParserInfo.Create(
                CreateRegions(node, operator_node),
                operator_info,
                expression_info,
            )

        # ----------------------------------------------------------------------

        return Callback
