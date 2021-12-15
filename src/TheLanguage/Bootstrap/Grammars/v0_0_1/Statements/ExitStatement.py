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

    from ....Parser.Statements.ExitStatementParserInfo import (
        ExpressionParserInfo,
        ExitStatementParserInfo,
    )


# ----------------------------------------------------------------------
class ExitStatement(GrammarPhrase):
    PHRASE_NAME                             = "Exit Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        # ----------------------------------------------------------------------
        def IsValidData(
            data: Phrase.StandardLexResultData,
        ) -> bool:
            return True

            # Any expression is valid here
            #
            # data = DynamicPhrase.SkipDynamicData(data)
            # assert isinstance(data, Phrase.StandardLexResultData), data
            #
            # # Are we looking at a right-recursive phrase where the last matched phrase is a
            # # func invocation?
            # if DynamicPhrase.IsRightRecursivePhrase(data.Phrase, DynamicPhrasesType.Expressions):
            #     assert isinstance(data.Data, Phrase.MultipleLexResultData), data.Data
            #
            #     data = cast(Phrase.StandardLexResultData, data.Data.DataItems[-1])
            #     data = DynamicPhrase.SkipDynamicData(data)
            #
            # # Are we looking at a func invocation?
            # if data.Phrase.Name == FuncInvocationExpression.PHRASE_NAME:
            #     return True
            #
            # return False

        # ----------------------------------------------------------------------

        super(ExitStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "exit",
                    ":",

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
            assert len(nodes) == 4

            # <func_invocation_expression>
            func_invocation_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[2])))
            func_invocation_info = cast(ExpressionParserInfo, GetParserInfo(func_invocation_node))

            return ExitStatementParserInfo(
                CreateParserRegions(node, func_invocation_node),  # type: ignore
                func_invocation_info,
            )

        # ----------------------------------------------------------------------

        return Impl
