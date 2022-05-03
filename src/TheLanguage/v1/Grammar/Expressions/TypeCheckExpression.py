# ----------------------------------------------------------------------
# |
# |  TypeCheckExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 14:55:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeCheckExpression object"""

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
        PhraseItem,
    )

    from ...Parser.Parser import CreateRegions, GetParserInfo

    from ...Parser.ParserInfos.Expressions.TypeCheckExpressionParserInfo import (
        ExpressionParserInfo,
        OperatorType,
        TypeCheckExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class TypeCheckExpression(GrammarPhrase):
    PHRASE_NAME                             = "Type Check Expression"

    OPERATOR_MAP                            = {
        "is" : OperatorType.Is,
        "is not" : OperatorType.IsNot,
    }

    assert len(OPERATOR_MAP) == len(OperatorType)

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TypeCheckExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # <expression>
                DynamicPhrasesType.Expressions,

                # <operator>
                PhraseItem(
                    name="Operator",
                    item=tuple(self.__class__.OPERATOR_MAP.keys()),
                ),

                # <type>
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
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # <operator>
            operator_node = cast(AST.Leaf, ExtractOr(cast(AST.Node, nodes[1])))
            operator_info = ExtractToken(
                operator_node,
                return_match_contents=True,
            )

            operator_info = cls.OPERATOR_MAP[operator_info]

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            type_info = cast(ExpressionParserInfo, GetParserInfo(type_node))

            return TypeCheckExpressionParserInfo.Create(
                CreateRegions(node, operator_node),
                operator_info,
                expression_info,
                type_info,
            )

        # ----------------------------------------------------------------------

        return Callback
