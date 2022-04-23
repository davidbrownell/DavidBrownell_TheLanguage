# ----------------------------------------------------------------------
# |
# |  UnaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 16:26:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the UnaryExpression object"""

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
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        Phrase as LexPhrase,
        PhraseItem,
    )

    from ...Parser.Parser import CreateRegions, GetParserInfo

    from ...Parser.ParserInfos.Expressions.UnaryExpressionParserInfo import (
        ExpressionParserInfo,
        OperatorType,
        UnaryExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class UnaryExpression(GrammarPhrase):
    PHRASE_NAME                             = "Unary Expression"

    OPERATOR_MAP                            = {
        "+": OperatorType.Positive,
        "-": OperatorType.Negative,

        "not": OperatorType.Not,
    }

    assert len(OPERATOR_MAP) == len(OperatorType)

    # ----------------------------------------------------------------------
    def __init__(self):
        super(UnaryExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # <operator>
                PhraseItem(
                    name="Operator",
                    item=tuple(self.__class__.OPERATOR_MAP.keys()),
                ),

                # <expression>
                DynamicPhrasesType.Expressions,
            ],
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
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return UnaryExpressionParserInfo.Create(
                CreateRegions(node, operator_node),
                operator_info,
                expression_info,
            )

        # ----------------------------------------------------------------------

        return Callback

    # ----------------------------------------------------------------------
    @classmethod
    def GetOperatorType(
        cls,
        data: LexPhrase.LexResultData,
    ) -> OperatorType:
        assert isinstance(data.data, list), data.data

        # The 1st valid data item is the operator
        for data_item in data.data:
            if isinstance(data_item, LexPhrase.TokenLexResultData) and data_item.is_ignored:
                continue

            assert isinstance(data_item, LexPhrase.LexResultData), data_item
            assert isinstance(data_item.data, LexPhrase.LexResultData), data_item.data

            data = data_item.data
            break

        assert isinstance(data.data, LexPhrase.TokenLexResultData), data.data
        token_data = data.data

        value = token_data.value.match.string[token_data.value.match.start() : token_data.value.match.end()]  # type: ignore
        return cls.OPERATOR_MAP[value]
