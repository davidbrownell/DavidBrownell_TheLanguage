# ----------------------------------------------------------------------
# |
# |  GroupCompileExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 14:37:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GroupCompileExpression object"""

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
        ExtractSequence,
    )

    from ...Parser.Parser import GetParserInfo

    from ...Parser.ParserInfos.CompileExpressions.UnaryCompileExpressionParserInfo import (
        CompileExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class GroupCompileExpression(GrammarPhrase):
    PHRASE_NAME                             = "Group CompileExpression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GroupCompileExpression, self).__init__(
            DynamicPhrasesType.CompileExpressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <expression>
                    DynamicPhrasesType.CompileExpressions,

                    # ')'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",
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
            assert len(nodes) == 5

            # <expression>
            expression_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            expression_info = cast(CompileExpressionParserInfo, GetParserInfo(expression_node))

            return expression_info

        # ----------------------------------------------------------------------

        return Callback
