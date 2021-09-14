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
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.Expressions.TernaryExpressionLexerInfo import (
        ExpressionLexerInfo,
        TernaryExpressionLexerData,
        TernaryExpressionLexerInfo,
        TernaryExpressionLexerRegions,
    )

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo

    from ....Parser.Phrases.DSL import (
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
    @classmethod
    @Interface.override
    def ExtractLexerInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 5

            # <expr> (True)
            true_node = ExtractDynamic(cast(Node, nodes[0]))
            true_data = cast(ExpressionLexerInfo, GetLexerInfo(true_node))

            # <expr> (Condition)
            cond_node = ExtractDynamic(cast(Node, nodes[2]))
            cond_data = cast(ExpressionLexerInfo, GetLexerInfo(cond_node))

            # <expr> (False)
            false_node = ExtractDynamic(cast(Node, nodes[4]))
            false_data = cast(ExpressionLexerInfo, GetLexerInfo(false_node))

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                TernaryExpressionLexerInfo(
                    TernaryExpressionLexerData(true_data, cond_data, false_data),
                    CreateLexerRegions(
                        TernaryExpressionLexerRegions,  # type: ignore
                        node,
                        true_node,
                        cond_node,
                        false_node,
                    ),
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
