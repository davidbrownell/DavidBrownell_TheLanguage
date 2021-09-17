# ----------------------------------------------------------------------
# |
# |  CastExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 11:25:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CastExpression object"""

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
    from ..Common import TypeModifier
    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.Expressions.CastExpressionLexerInfo import (
        CastExpressionLexerInfo,
        ExpressionLexerInfo,
        TypeLexerInfo,
    )

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOr,
        ExtractSequence,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class CastExpression(GrammarPhrase):
    """\
    Casts a variable to a different type.

    <expr> 'as' <modifier> | <type>

    Examples:
        foo = bar as Int
        biz = baz as Int val
        another = a_var as val
    """

    PHRASE_NAME                             = "Cast Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(CastExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # 'as'
                    "as",

                    # <modifier> | <type>
                    PhraseItem(
                        name="Type or Modifier",
                        item=(
                            # <modifier>
                            PhraseItem(
                                name="Modifier",
                                item=TypeModifier.CreatePhraseItem(),
                            ),

                            # <type>
                            DynamicPhrasesType.Types,
                        ),
                    ),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractLexerInfo(
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractLexerInfoResult]:
        # ----------------------------------------------------------------------
        def CreateLexerInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <expr>
            expr_node = ExtractDynamic(cast(Node, nodes[0]))
            expr_info = cast(ExpressionLexerInfo, GetLexerInfo(expr_node))

            # <modifier> | <type>
            type_node = cast(Node, ExtractOr(cast(Node, nodes[2])))

            assert type_node.Type is not None
            if type_node.Type.Name == "Modifier":
                type_info = TypeModifier.Extract(type_node)
            else:
                type_info = cast(TypeLexerInfo, GetLexerInfo(ExtractDynamic(type_node)))

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                CastExpressionLexerInfo(
                    CreateLexerRegions(node, expr_node, type_node),  # type: ignore
                    expr_info,
                    type_info,  # type: ignore
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
