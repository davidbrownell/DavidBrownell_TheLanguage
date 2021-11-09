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
    from ..Common import Tokens as CommonTokens

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
    )

    from ....Parser.Parser import CreateParserRegions

    from ....Parser.Types.TypeOfTypeParserInfo import TypeOfTypeParserInfo


# ----------------------------------------------------------------------
class TypeOfType(GrammarPhrase):

    PHRASE_NAME                             = "TypeOf Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(TypeOfType, self).__init__(
            DynamicPhrasesType.Types,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    "TypeOf'",
                    "(",

                    # <name>
                    CommonTokens.GenericName,

                    ")",
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: AST.Node
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 4

        # <name>
        name_leaf = cast(AST.Leaf, nodes[2])
        name_info = cast(str, ExtractToken(name_leaf))

        return TypeOfTypeParserInfo(
            CreateParserRegions(node, name_leaf),  # type: ignore
            name_info,
        )
