# ----------------------------------------------------------------------
# |
# |  FuncInvocationExpression.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 08:27:08
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

from typing import Callable, cast, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import ArgumentsPhraseItem

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractSequence,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo
    from ....Parser.Expressions.FuncInvocationExpressionParserInfo import (
        ExpressionParserInfo,
        FuncInvocationExpressionParserInfo,
    )


# ----------------------------------------------------------------------
class FuncInvocationExpression(GrammarPhrase):
    """\
    A function invocation.

    <expression> <<Arguments>>

    Examples:
        Func1()
        Func2(a,)
        Func3(a, b, c)
        Func4(a, b, c=foo)
        Func5(
            a,
            b,
            c,
            d,
            e,
        )
    """

    PHRASE_NAME                             = "Func Invocation Expression"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(FuncInvocationExpression, self).__init__(
            DynamicPhrasesType.Expressions,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <expression>
                    DynamicPhrasesType.Expressions,

                    # <<Arguments>>
                    ArgumentsPhraseItem.Create(),
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
            assert len(nodes) == 2

            # <expression>
            expression_node = ExtractDynamic(cast(AST.Node, nodes[0]))
            expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

            # <<Arguments>>
            arguments_node = cast(AST.Node, nodes[1])
            arguments_info = ArgumentsPhraseItem.ExtractParserInfo(arguments_node)

            return FuncInvocationExpressionParserInfo(
                CreateParserRegions(node, expression_node, arguments_node),  # type: ignore
                expression_info,
                arguments_info,
            )

        # ----------------------------------------------------------------------

        return Impl
