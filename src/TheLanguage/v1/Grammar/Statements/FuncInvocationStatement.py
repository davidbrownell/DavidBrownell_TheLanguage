# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-22 08:37:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationStatement object"""

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
    from ..Expressions.CallExpression import CallExpression

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
        PhraseItem,
    )

    from ...Lexer.Phrases.DynamicPhrase import DynamicPhrase, Phrase

    from ...Parser.Parser import GetParserInfo

    from ...Parser.ParserInfos.Expressions.ExpressionParserInfo import (
        ExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class FuncInvocationStatement(GrammarPhrase):
    PHRASE_NAME                             = "Func Invocation Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        # ----------------------------------------------------------------------
        def IsValidData(
            data: Phrase.LexResultData,
        ) -> bool:
            data = DynamicPhrase.GetDynamicData(data)

            return data.phrase.name == CallExpression.PHRASE_NAME

        # ----------------------------------------------------------------------

        super(FuncInvocationStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                # <expression>
                PhraseItem(
                    item=DynamicPhrasesType.Expressions,
                    is_valid_data_func=IsValidData,
                ),

                CommonTokens.Newline,
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
            assert len(nodes) == 2

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return expression_info

        # ----------------------------------------------------------------------

        return Callback
