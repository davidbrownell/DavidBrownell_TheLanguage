# ----------------------------------------------------------------------
# |
# |  FuncInvocationExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 19:38:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationExpression object"""

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
    from ..Common import ArgumentsPhraseItem
    from ...GrammarPhrase import CreateParserRegions, GrammarPhrase

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractSequence,
        Node,
    )

    from ....Parser.Expressions.FuncInvocationExpressionParserInfo import (
        ExpressionParserInfo,
        FuncInvocationExpressionParserInfo,
    )
    from ....Parser.ParserInfo import GetParserInfo, SetParserInfo


# ----------------------------------------------------------------------
class FuncInvocationExpression(GrammarPhrase):
    """\
    A function invocation.

    <expr> <<Arguments>>

    Examples:
        Func1()
        Func2(a,)
        Func3(a, b, c)
        Func4(a, b, c=foo)
    """

    PHRASE_NAME                             = "Func Invocation Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncInvocationExpression, self).__init__(
            GrammarPhrase.Type.Expression,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expr>
                    DynamicPhrasesType.Expressions,

                    # Arguments
                    ArgumentsPhraseItem.Create(),
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def ExtractParserInfo(
        cls,
        node: Node,
    ) -> Optional[GrammarPhrase.ExtractParserInfoResult]:
        # ----------------------------------------------------------------------
        def CreateParserInfo():
            nodes = ExtractSequence(node)
            assert len(nodes) in [2, 3], nodes

            # <expr>
            expression_node = ExtractDynamic(cast(Node, nodes[0]))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # Arguments
            arguments_node = cast(Node, nodes[1])
            arguments_info = ArgumentsPhraseItem.ExtractParserInfo(arguments_node)
            if arguments_info is None:
                arguments_node = None

            # pylint: disable=too-many-function-args
            SetParserInfo(
                node,
                FuncInvocationExpressionParserInfo(
                    CreateParserRegions(node, expression_node, arguments_node),  # type: ignore
                    expression_info,
                    arguments_info,
                ),
            )

        # ----------------------------------------------------------------------

        return GrammarPhrase.ExtractParserInfoResult(CreateParserInfo)
