# ----------------------------------------------------------------------
# |
# |  GroupExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 16:32:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GroupExpression object"""

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

    from ...Parser.ParserInfos.Expressions.ExpressionParserInfo import (
        ExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class GroupExpression(GrammarPhrase):
    PHRASE_NAME                             = "Group Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GroupExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <expression>
                    DynamicPhrasesType.Expressions,

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
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return expression_info

        # ----------------------------------------------------------------------

        return Callback
