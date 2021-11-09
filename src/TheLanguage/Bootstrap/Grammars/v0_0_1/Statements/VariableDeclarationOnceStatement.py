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

    from ..Common import TypeModifier

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractSequence,
        ExtractToken,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo

    from ....Parser.Statements.VariableDeclarationOnceStatementParserInfo import (
        VariableDeclarationOnceStatementParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
class VariableDeclarationOnceStatement(GrammarPhrase):

    PHRASE_NAME                             = "Variable Declaration Once Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(VariableDeclarationOnceStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <type>
                    DynamicPhrasesType.Types,

                    # 'once'
                    "once",

                    # <name>
                    CommonTokens.GenericLowerName,

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

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[0])))
            type_info = cast(TypeParserInfo, GetParserInfo(type_node))

            # <name>
            name_leaf = cast(AST.Leaf, nodes[2])
            name_info = cast(str, ExtractToken(name_leaf))

            if not CommonTokens.VariableNameRegex.match(name_info):
                raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "variable")

            return VariableDeclarationOnceStatementParserInfo(
                CreateParserRegions(node, type_node, name_leaf), # type: ignore
                type_info,
                name_info,
            )

        # ----------------------------------------------------------------------

        return Impl
