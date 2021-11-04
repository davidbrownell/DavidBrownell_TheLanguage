import itertools
import os

from typing import Callable, cast, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common import Tokens as CommonTokens
    from ...Common import TypeModifier

    from ....GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from .....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        OptionalPhraseItem,
        ZeroOrMorePhraseItem,
    )

    from .....Parser.Parser import CreateParserRegions, GetParserInfo

    from .....Parser.Types.VariantTypeParserInfo import (
        TypeParserInfo,
        VariantTypeParserInfo,
    )


# ----------------------------------------------------------------------
class VariantTypeImpl(GrammarPhrase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase_name: str,
        dynamic_phrases_type: DynamicPhrasesType,
    ):
        super(VariantTypeImpl, self).__init__(
            dynamic_phrases_type,
            CreatePhrase(
                name=phrase_name,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <type> '|'
                    dynamic_phrases_type,
                    "|",

                    ZeroOrMorePhraseItem.Create(
                        name="Type and Sep",
                        item=[
                            dynamic_phrases_type,
                            "|",
                        ],
                    ),

                    # <type>
                    dynamic_phrases_type,

                    # ')'
                    CommonTokens.PopIgnoreWhitespaceControl,
                    ")",

                    # <modifier>?
                    OptionalPhraseItem.Create(
                        name="Modifier",
                        item=TypeModifier.CreatePhraseItem(),
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
            assert len(nodes) == 9

            type_infos: List[TypeParserInfo] = []

            for child_node in itertools.chain(
                [nodes[2]],
                [
                    ExtractSequence(delimited_node)[0]
                    for delimited_node in cast(
                        List[AST.Node],
                        ExtractRepeat(cast(AST.Node, nodes[4])),
                    )
                ],
                [nodes[5]],
            ):
                type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, child_node)))
                type_info = cast(TypeParserInfo, GetParserInfo(type_node))

                type_infos.append(type_info)

            # <type_modifier>?
            type_modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[8])))
            if type_modifier_node is None:
                type_modifier_info = None
            else:
                type_modifier_info = TypeModifier.Extract(type_modifier_node)

            return VariantTypeParserInfo(
                CreateParserRegions(node, type_modifier_node),  # type: ignore
                type_infos,
                type_modifier_info,
            )


        # ----------------------------------------------------------------------

        return Impl
