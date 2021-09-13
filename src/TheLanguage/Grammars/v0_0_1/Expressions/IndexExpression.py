# ----------------------------------------------------------------------
# |
# |  IndexExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-26 16:00:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IndexExpression object"""

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

    from ....Lexer.Expressions.IndexExpressionLexerInfo import (
        ExpressionLexerInfo,
        IndexExpressionLexerData,
        IndexExpressionLexerInfo,
        IndexExpressionLexerRegions,
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
class IndexExpression(GrammarPhrase):
    """\
    Applies an index operation to an expression.

    <expr> '[' <expr> ']'

    Examples:
        foo[1]
        bar[(1, 2)]
    """

    PHRASE_NAME                             = "Index Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(IndexExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # '['
                    "[",

                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # ']'
                    "]",
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
            assert len(nodes) == 4

            # <expr>
            prefix_node = cast(Node, ExtractDynamic(cast(Node, nodes[0])))
            prefix_data = cast(ExpressionLexerInfo, GetLexerInfo(prefix_node))

            # <expr>
            index_node = cast(Node, ExtractDynamic(cast(Node, nodes[2])))
            index_data = cast(ExpressionLexerInfo, GetLexerInfo(index_node))

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                IndexExpressionLexerInfo(
                    IndexExpressionLexerData(prefix_data, index_data),
                    CreateLexerRegions(
                        IndexExpressionLexerRegions,  # type: ignore
                        node,
                        prefix_node,
                        index_node,
                    ),
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
