# ----------------------------------------------------------------------
# |
# |  GroupExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-23 10:58:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GroupExpression object"""

import os

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import CreateParserRegions, GrammarPhrase

    from ....Parser.Expressions.GroupExpressionParserInfo import (
        ExpressionParserInfo,
        GroupExpressionParserInfo,
    )

    from ....Parser.ParserInfo import GetParserInfo, SetParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
        Node,
    )


# ----------------------------------------------------------------------
class GroupExpression(GrammarPhrase):
    """
    Groups an expression.

    '(' <expr> ')'

    Examples:
        (one + two) + three
        one or (two and three)
    """

    PHRASE_NAME                             = "Group Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GroupExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <expr>
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
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        # ----------------------------------------------------------------------
        def CreateParserInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            # <expr>
            expression_node = ExtractDynamic(cast(Node, nodes[2]))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # pylint: disable=too-many-function-args
            SetParserInfo(
                node,
                GroupExpressionParserInfo(
                    CreateParserRegions(node, expression_node),  # type: ignore
                    expression_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
