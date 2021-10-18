# ----------------------------------------------------------------------
# |
# |  GeneratorExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 09:56:09
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

from typing import Callable, cast, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TernaryExpression import TernaryExpression

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        OptionalPhraseItem,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Expressions.GeneratorExpressionParserInfo import (
        ExpressionParserInfo,
        GeneratorExpressionParserInfo,
        NameParserInfo,
    )


# ----------------------------------------------------------------------
class GeneratorExpression(GrammarPhrase):
    """\
    Expression that generates values.

    <expression> 'for' <name> 'in' <expression> ('if' <expression>)?

    Examples:
        AddOne(value) for value in OneToTen()
        AddOne(value) for value in OneToTen() if value % 2 == 0
    """

    PHRASE_NAME                             = "Generator Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(GeneratorExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # 'for'
                    "for",

                    # <name>
                    DynamicPhrasesType.Names,

                    # 'in'
                    "in",

                    # <expression>
                    PhraseItem.Create(
                        item=DynamicPhrasesType.Expressions,

                        # Don't let the TernaryExpression capture the 'if' token that may follow, as
                        # the TernaryExpression requires an 'else' clause. This will never match
                        # here, as there will never be an else clause prior to the 'if' below.
                        exclude_phrases=[TernaryExpression.PHRASE_NAME],
                    ),

                    # ('if' <expression>)?
                    OptionalPhraseItem.Create(
                        name="Conditional",
                        item=[
                            "if",
                            DynamicPhrasesType.Expressions,
                        ],
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
            assert len(nodes) == 6

            # <expression>: Result
            result_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            result_info = cast(ExpressionParserInfo, GetParserInfo(result_node))

            # <name>
            name_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            name_info = cast(NameParserInfo, GetParserInfo(name_node))

            # <expression>: Source
            source_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[4])))
            source_info = cast(ExpressionParserInfo, GetParserInfo(source_node))

            # ('if' <expression>)?
            conditional_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[5])))

            if conditional_node is None:
                conditional_info = None
            else:
                conditional_nodes = ExtractSequence(conditional_node)
                assert len(conditional_nodes) == 2

                conditional_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, conditional_nodes[1])))
                conditional_info = cast(ExpressionParserInfo, GetParserInfo(conditional_node))

            return GeneratorExpressionParserInfo(
                CreateParserRegions(node, result_node, name_node, source_node, conditional_node),  # type: ignore
                result_info,
                name_info,
                source_info,
                conditional_info,
            )

        # ----------------------------------------------------------------------

        return Impl
