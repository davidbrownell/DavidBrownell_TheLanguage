# ----------------------------------------------------------------------
# |
# |  BinaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 16:35:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BinaryExpression object"""

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

    from ...Parser.ParserInfos.Expressions.BinaryExpressionParserInfo import (
        BinaryExpressionParserInfo,
        ExpressionParserInfo,
        OperatorType,
    )


# ----------------------------------------------------------------------
class BinaryExpression(GrammarPhrase):
    PHRASE_NAME                             = "Binary Expression"

    OPERATOR_MAP                            = {
        "*": OperatorType.Multiply,
        "/": OperatorType.Divide,
        "//": OperatorType.DivideFloor,
        "%": OperatorType.Modulus,
        "**": OperatorType.Power,

        "+": OperatorType.Add,
        "-": OperatorType.Subtract,

        "<<": OperatorType.BitShiftLeft,
        ">>": OperatorType.BitShiftRight,

        "&": OperatorType.BitwiseAnd,

        "^": OperatorType.BitwiseXor,

        "|": OperatorType.BitwiseOr,

        "<": OperatorType.Less,
        "<=": OperatorType.LessEqual,
        ">": OperatorType.Greater,
        ">=": OperatorType.GreaterEqual,
        "==": OperatorType.Equal,
        "!=": OperatorType.NotEqual,

        "and": OperatorType.LogicalAnd,

        "or": OperatorType.LogicalOr,

    }

    assert len(OPERATOR_MAP) == len(OperatorType), (len(OPERATOR_MAP), len(OperatorType))

    # ----------------------------------------------------------------------
    def __init__(self):
        super(BinaryExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # <expression>
                DynamicPhrasesType.Expressions,

                # <operator>
                PhraseItem(
                    name="Operator",
                    item=tuple(self.__class__.OPERATOR_MAP),
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
            assert len(nodes) == 3

            # <expression>
            left_expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            left_expression_info = cast(ExpressionParserInfo, GetParserInfo(left_expression_node))

            # <operator>
            operator_node = cast(AST.Leaf, ExtractOr(cast(AST.Node, nodes[1])))
            operator_info = ExtractToken(
                operator_node,
                return_match_contents=True,
            )

            operator_info = cls.OPERATOR_MAP[operator_info]

            # <expression>
            right_expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            right_expression_info = cast(ExpressionParserInfo, GetParserInfo(right_expression_node))

            return BinaryExpressionParserInfo.Create(
                CreateRegions(node, operator_node),
                left_expression_info,
                operator_info,
                right_expression_info,
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

        # The 2nd valid data item is the operator
        item_ctr = 0

        for data_item in data.data:
            if isinstance(data_item, LexPhrase.TokenLexResultData) and data_item.is_ignored:
                continue

            assert isinstance(data_item, LexPhrase.LexResultData), data_item

            item_ctr += 1

            if item_ctr == 2:
                assert isinstance(data_item.data, LexPhrase.LexResultData), data_item.data
                data = data_item.data

                break

        assert isinstance(data.data, LexPhrase.TokenLexResultData), data.data
        token_data = data.data

        value = token_data.value.match.string[token_data.value.match.start() : token_data.value.match.end()]  # type: ignore
        return cls.OPERATOR_MAP[value]
