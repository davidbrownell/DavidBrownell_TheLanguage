# ----------------------------------------------------------------------
# |
# |  CastExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 09:25:46
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

from typing import Callable, cast, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import TypeModifier

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOr,
        ExtractSequence,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Expressions.CastExpressionParserInfo import (
        CastExpressionParserInfo,
        ExpressionParserInfo,
        TypeParserInfo,

        # The following imports are not used in this file but are here as a
        # convenience
        InvalidModifierError,
        TypeWithModifierError,
    )


# ----------------------------------------------------------------------
class CastExpression(GrammarPhrase):
    """\
    Casts an expression to a different type.

    <expression> 'as' <modifier> | <type.

    Examples:
        bar as Int
        baz as val
    """

    PHRASE_NAME                             = "Cast Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(CastExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # 'as'
                    "as",

                    # <modifier> | <type>
                    PhraseItem.Create(
                        name="Type or Modifier",
                        item=(
                            # <modifier>
                            PhraseItem.Create(
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
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 3

            # <expression>
            expression_node = ExtractDynamic(cast(AST.Node, nodes[0]))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # <modifier> | <type>
            type_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[2])))

            assert type_node.Type is not None
            if type_node.Type.Name == "Modifier":
                type_info = TypeModifier.Extract(type_node)
            else:
                type_info = cast(TypeParserInfo, GetParserInfo(ExtractDynamic(type_node)))

            return CastExpressionParserInfo(
                CreateParserRegions(node, expression_node, type_node),  # type: ignore
                expression_info,
                type_info,
            )

        # ----------------------------------------------------------------------

        return Impl
