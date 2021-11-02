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
    from .. import ConstraintArgumentsPhraseItem
    from .. import TemplateArgumentsPhraseItem
    from .. import Tokens as CommonTokens
    from .. import TypeModifier

    from ....GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from .....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
    )

    from .....Parser.Parser import CreateParserRegions
    from .....Parser.Types.StandardTypeParserInfo import StandardTypeParserInfo


# ----------------------------------------------------------------------
class StandardTypeImpl(GrammarPhrase):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase_name: str,
        dynamic_phrases_type: DynamicPhrasesType,
    ):
        super(StandardTypeImpl, self).__init__(
            dynamic_phrases_type,
            CreatePhrase(
                name=phrase_name,
                item=[
                    # <generic_name>
                    CommonTokens.GenericUpperName,

                    # <templates>?
                    OptionalPhraseItem.Create(
                        name="Template Arguments",
                        item=TemplateArgumentsPhraseItem.Create(),
                    ),

                    # <constraints>?
                    OptionalPhraseItem.Create(
                        name="Constraint Arguments",
                        item=ConstraintArgumentsPhraseItem.Create(),
                    ),

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
            assert len(nodes) == 4

            # <generic_name>
            type_leaf = cast(AST.Leaf, nodes[0])
            type_info = cast(str, ExtractToken(type_leaf))

            if not CommonTokens.TypeNameRegex.match(type_info):
                raise CommonTokens.InvalidTokenError.FromNode(type_leaf, type_info, "type")

            # <templates>?
            templates_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[1])))
            if templates_node is None:
                templates_info = None
            else:
                templates_info = TemplateArgumentsPhraseItem.ExtractParserInfo(templates_node)

            # <constraints>?
            constraints_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[2])))
            if constraints_node is None:
                constraints_info = None
            else:
                constraints_info = ConstraintArgumentsPhraseItem.ExtractParserInfo(constraints_node)

            # <modifier>?
            modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[3])))

            if modifier_node is None:
                modifier_info = None
            else:
                modifier_info = TypeModifier.Extract(modifier_node)

            return StandardTypeParserInfo(
                CreateParserRegions(node, type_leaf, templates_node, constraints_node, modifier_node),  # type: ignore
                type_info,
                templates_info,
                constraints_info,
                modifier_info,
            )

        # ----------------------------------------------------------------------

        return Impl
