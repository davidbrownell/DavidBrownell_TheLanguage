# ----------------------------------------------------------------------
# |
# |  LambdaExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-28 11:10:21
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

from typing import cast, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import ParametersPhraseItem

    from ...GrammarPhrase import CreateLexerRegions, GrammarPhrase

    from ....Lexer.Expressions.LambdaExpressionLexerInfo import (
        ExpressionLexerInfo,
        LambdaExpressionLexerInfo,
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
class LambdaExpression(GrammarPhrase):
    """\
    Creates a temporary function.

    'lambda' <parameters_phrase_item> ':' <expr>

    Examples:
        lambda (Int a, Char b): b * a
        lambda (): 10
    """

    PHRASE_NAME                             = "Lambda Expression"

    # TODO: Captures

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        super(LambdaExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'lambda'
                    "lambda",

                    # <parameters>
                    ParametersPhraseItem.Create(),

                    # ':'
                    ":",

                    # <expr>
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
            assert len(nodes) == 4

            # <parameters>
            parameters_node, parameters_info = ParametersPhraseItem.ExtractLexerInfo(cast(Node, nodes[1]))

            # <expr>
            expression_node = ExtractDynamic(cast(Node, nodes[3]))
            expression_info = cast(ExpressionLexerInfo, GetLexerInfo(expression_node))

            # pylint: disable=too-many-function-args
            SetLexerInfo(
                node,
                LambdaExpressionLexerInfo(
                    CreateLexerRegions(node, parameters_node, expression_node),  # type: ignore
                    parameters_info,
                    expression_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractLexerInfoResult(CreateLexerInfo)
