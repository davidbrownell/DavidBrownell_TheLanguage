# ----------------------------------------------------------------------
# |
# |  CallExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-22 08:22:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CallExpression object"""

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

    from ..Common import FuncArgumentsFragment

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
    )

    from ...Parser.Parser import CreateRegions, GetParserInfo

    from ...Parser.ParserInfos.Expressions.CallExpressionParserInfo import (
        CallExpressionParserInfo,
        ExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class CallExpression(GrammarPhrase):
    PHRASE_NAME                             = "Call Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(CallExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            self.PHRASE_NAME,
            [
                # <expression>
                DynamicPhrasesType.Expressions,

                # <FuncArgumentsFragment>
                FuncArgumentsFragment.Create(),
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

            # <FuncArgumentsFragment>
            arguments_node = cast(AST.Node, cast(AST.Node, nodes[1]))
            arguments_info = FuncArgumentsFragment.Extract(arguments_node)

            return CallExpressionParserInfo.Create(
                CreateRegions(node, arguments_node),
                expression_info,
                arguments_info,
            )

        # ----------------------------------------------------------------------

        return Callback
