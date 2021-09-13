# ----------------------------------------------------------------------
# |
# |  GeneratorExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 19:13:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GeneratorExpression object"""

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
    from .TernaryExpression import TernaryExpression

    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.Expressions.GeneratorExpressionLexerInfo import (
        ExpressionLexerInfo,
        GeneratorExpressionLexerData,
        GeneratorExpressionLexerInfo,
        GeneratorExpressionLexerRegions,
        NameLexerInfo,
    )

    from ....Lexer.LexerInfo import GetLexerInfo, SetLexerInfo

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
class GeneratorExpression(GrammarPhrase):
    """\
    Expression that generates values.

    <expr> 'for' <name> 'in' <expr> ('if' <expr>)?

    Examples:
        AddOne(value) for value in OneToTen()
        AddOne(value) for value in OneToTen() if value % 2 == 0
    """

    PHRASE_NAME                             = "Generator Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GeneratorExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # 'for'
                    "for",

                    # <name>
                    DynamicPhrasesType.Names,

                    # 'in'
                    "in",

                    # <expr>
                    PhraseItem(
                        item=DynamicPhrasesType.Expressions,

                        # Don't let the TernaryExpression capture the 'if' token that may follow, as
                        # the TernaryExpression expects an 'else' clause, but the following 'if' will
                        # never have one.
                        exclude=[TernaryExpression.PHRASE_NAME],
                    ),

                    # ('if' <expr>)?
                    PhraseItem(
                        name="Conditional",
                        item=[
                            # 'if'
                            "if",

                            # <expr>
                            DynamicPhrasesType.Expressions,
                        ],
                        arity="?",
                    ),
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
            assert len(nodes) == 6

            # <expr>
            display_node = cast(Node, ExtractDynamic(cast(Node, nodes[0])))
            display_info = cast(ExpressionLexerInfo, GetLexerInfo(display_node))

            # <name>
            name_node = cast(Node, ExtractDynamic(cast(Node, nodes[2])))
            name_info = cast(NameLexerInfo, GetLexerInfo(name_node))

            # <expr>
            source_node = cast(Node, ExtractDynamic(cast(Node, nodes[4])))
            source_info = cast(ExpressionLexerInfo, GetLexerInfo(source_node))

            # ('if' <expr>)?
            conditional_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[5])))

            if conditional_node is not None:
                conditional_nodes = ExtractSequence(conditional_node)
                assert len(conditional_nodes) == 2

                expr_node = cast(Node, ExtractDynamic(cast(Node, conditional_nodes[1])))
                conditional_info = cast(ExpressionLexerInfo, GetLexerInfo(expr_node))
            else:
                conditional_info = None

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                GeneratorExpressionLexerInfo(
                    GeneratorExpressionLexerData(
                        display_info,
                        name_info,
                        source_info,
                        conditional_info,
                    ),
                    CreateLexerRegions(
                        GeneratorExpressionLexerRegions,  # type: ignore
                        node,
                        display_node,
                        name_node,
                        source_node,
                        conditional_node,
                    ),
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
