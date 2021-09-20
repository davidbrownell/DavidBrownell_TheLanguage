# ----------------------------------------------------------------------
# |
# |  TernaryExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 19:28:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TernaryExpression object"""

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
    from ...GrammarPhrase import CreateParserRegions, GrammarPhrase

    from ....Parser.Expressions.TernaryExpressionParserInfo import (
        ExpressionParserInfo,
        TernaryExpressionParserInfo,
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
class TernaryExpression(GrammarPhrase):
    """\
    Expression that yields on value on True and a different value on False.

    <expr> 'if' <expr> 'else' <expr>

    Examples:
        "The Truth" if SomeExpr() else "The Lie"
    """

    PHRASE_NAME                             = "Ternary Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TernaryExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    DynamicPhrasesType.Expressions,
                    "if",
                    DynamicPhrasesType.Expressions,
                    "else",
                    DynamicPhrasesType.Expressions,
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

            # <expr> (True)
            true_node = ExtractDynamic(cast(Node, nodes[0]))
            true_info = cast(ExpressionParserInfo, GetParserInfo(true_node))

            # <expr> (Condition)
            cond_node = ExtractDynamic(cast(Node, nodes[2]))
            cond_info = cast(ExpressionParserInfo, GetParserInfo(cond_node))

            # <expr> (False)
            false_node = ExtractDynamic(cast(Node, nodes[4]))
            false_info = cast(ExpressionParserInfo, GetParserInfo(false_node))

            # pylint: disable=too-many-function-args
            SetParserInfo(
                node,
                TernaryExpressionParserInfo(
                    CreateParserRegions(node, true_node, cond_node, false_node),  # type: ignore
                    true_info,
                    cond_info,
                    false_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
