# ----------------------------------------------------------------------
# |
# |  LambdaExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-07 15:31:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LambdaExpression object"""

import os

from typing import Callable, cast, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import ParametersPhraseItem

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractSequence,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Expressions.LambdaExpressionParserInfo import (
        ExpressionParserInfo,
        LambdaExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class LambdaExpression(GrammarPhrase):
    """\
    Creates a single-line anonymous function.

    'lambda' <<parameters>> ':' <expression>

    Examples:
        lambda (Int a, Char b): b * a
        lambda (): 10
    """

    PHRASE_NAME                             = "Lambda Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(LambdaExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'lambda'
                    "lambda",

                    # <<parameters>>
                    ParametersPhraseItem.Create(),

                    # ':'
                    ":",

                    # <expression>
                    DynamicPhrasesType.Expressions,
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
    ]:
        # ----------------------------------------------------------------------
        def Impl():
            nodes = ExtractSequence(node)
            assert len(nodes) == 4

            # <<parameters>>
            parameters_node = cast(AST.Node, nodes[1])
            parameters_info = ParametersPhraseItem.ExtractParserInfo(parameters_node)

            # <expression>
            expression_node = ExtractDynamic(cast(AST.Node, nodes[3]))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            return LambdaExpressionParserInfo(
                CreateParserRegions(node, parameters_node, expression_node),  # type: ignore
                parameters_info,
                expression_info,
            )

        # ----------------------------------------------------------------------

        return Impl
