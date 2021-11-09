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
    from ..Common import StatementsPhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common.TypeModifier import TypeModifier

    from ..Expressions.CastExpression import CastExpression

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractSequence,
        ExtractToken,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.ScopedStatementParserInfo import (
        ExpressionParserInfo,
        ScopedStatementParserInfo,
    )


# ----------------------------------------------------------------------
class ScopedStatement(GrammarPhrase):
    PHRASE_NAME                             = "Scoped Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(ScopedStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "with",

                    CommonTokens.GenericLowerName,

                    "=",

                    PhraseItem.Create(
                        item=DynamicPhrasesType.Expressions,
                        exclude_phrases=[CastExpression.PHRASE_NAME],
                    ),

                    StatementsPhraseItem.Create(),
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
            assert len(nodes) == 5

            # <name>
            name_leaf = cast(AST.Leaf, nodes[1])
            name_info = cast(str, ExtractToken(name_leaf))

            if not CommonTokens.VariableNameRegex.match(name_info):
                raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "variable")

            # <expr>
            expr_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[3])))
            expr_info = cast(ExpressionParserInfo, GetParserInfo(expr_node))

            # <statement>+
            statements_node = cast(AST.Node, nodes[4])
            statements_info = StatementsPhraseItem.ExtractParserInfo(statements_node)

            return ScopedStatementParserInfo(
                CreateParserRegions(node, expr_node, name_leaf, statements_node),  # type: ignore
                expr_info,
                name_info,
                statements_info,
            )

        # ----------------------------------------------------------------------

        return Impl
