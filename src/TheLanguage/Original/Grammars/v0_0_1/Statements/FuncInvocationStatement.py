# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-17 18:37:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationStatement object"""

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
    from ..Common import Tokens as CommonTokens

    from ..Expressions.FuncInvocationExpression import (
        FuncInvocationExpression,

        # ...GrammarInfo
        AST,
        DynamicPhrasesType,
        GrammarPhrase,
        ParserInfo,

        # ....Lexer.Phrases.DSL
        CreatePhrase,
        ExtractDynamic,
        ExtractSequence,

        # ....Parser.Parser
        CreateParserRegions,
        GetParserInfo,

        # ....Parser.Expressions.FuncInvocationExpressionParserInfo
        FuncInvocationExpressionParserInfo,

    )

    from ....Lexer.Components.Phrase import Phrase
    from ....Lexer.Phrases.DSL import PhraseItem
    from ....Lexer.Phrases.DynamicPhrase import DynamicPhrase
    from ....Lexer.Phrases.OrPhrase import OrPhrase

    from ....Parser.Statements.FuncInvocationStatementParserInfo import (
        ExpressionParserInfo,
        FuncInvocationStatementParserInfo,
    )


# ----------------------------------------------------------------------
class FuncInvocationStatement(GrammarPhrase):
    """\
    Invocation of a function that ignores the return value.

    <func_invocation_expression> <newline>

    Examples:
        Int Foo():
            Bar() # <--- Invokes Bar
    """

    PHRASE_NAME                             = "Func Invocation Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        # ----------------------------------------------------------------------
        def IsValidData(
            data: Phrase.StandardLexResultData,
        ) -> bool:
            data = DynamicPhrase.SkipDynamicData(data)
            assert isinstance(data, Phrase.StandardLexResultData), data

            # Are we looking at a right-recursive phrase where the last matched phrase is a
            # func invocation?
            if DynamicPhrase.IsRightRecursivePhrase(data.Phrase, DynamicPhrasesType.Expressions):
                assert isinstance(data.Data, Phrase.MultipleLexResultData), data.Data

                data = cast(Phrase.StandardLexResultData, data.Data.DataItems[-1])
                data = DynamicPhrase.SkipDynamicData(data)

            # Are we looking at a func invocation?
            if data.Phrase.Name == FuncInvocationExpression.PHRASE_NAME:
                return True

            return False

        # ----------------------------------------------------------------------

        super(FuncInvocationStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <func_invocation_expression>
                    PhraseItem.Create(
                        item=DynamicPhrasesType.Expressions,
                        is_valid_data_func=IsValidData,
                    ),

                    CommonTokens.Newline,
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
            assert len(nodes) == 2

            # <func_invocation_expression>
            func_invocation_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            func_invocation_info = cast(ExpressionParserInfo, GetParserInfo(func_invocation_node))

            return FuncInvocationStatementParserInfo(
                CreateParserRegions(node, func_invocation_node),  # type: ignore
                func_invocation_info,
            )

        # ----------------------------------------------------------------------

        return Impl
