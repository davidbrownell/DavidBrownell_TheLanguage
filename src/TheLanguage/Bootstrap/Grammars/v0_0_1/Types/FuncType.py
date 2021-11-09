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
    from ..Common import AttributePhraseItem
    from ..Common import Tokens as CommonTokens
    from ..Common import TypeModifier

    from ...GrammarInfo import AST, DynamicPhrasesType, GrammarPhrase, ParserInfo

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractDynamic,
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo
    from ....Parser.Types.FuncTypeParserInfo import (
        FunctionParameterTypeParserInfo,
        FuncTypeParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
class FuncType(GrammarPhrase):

    PHRASE_NAME                             = "Func Type"

    # ----------------------------------------------------------------------
    def __init__(self):
        type_only_parameter_phrase_item = PhraseItem.Create(
            name="Type Only Parameter",
            item=[
                # <type>
                DynamicPhrasesType.Types,

                # '*'?
                OptionalPhraseItem.Create(
                    name="Variadic",
                    item="*",
                ),

            ],
        )

        type_only_parameters_phrase_item = PhraseItem.Create(
            name="Type Only Parameters",
            item=[
                # '('
                "(",
                CommonTokens.PushIgnoreWhitespaceControl,

                # (<type_only_parameter_phrase_item> (',' <type_only_parameter_phrase_item>)* ',')?
                OptionalPhraseItem.Create(
                    item=[
                        # <type_only_parameter_phrase_item>
                        type_only_parameter_phrase_item,

                        ZeroOrMorePhraseItem.Create(
                            name="Comma and Type Only Parameter",
                            item=[
                                ",",
                                type_only_parameter_phrase_item,
                            ],
                        ),

                        # ','?
                        OptionalPhraseItem.Create(
                            name="Trailing Comma",
                            item=",",
                        ),
                    ],
                ),

                # ')'
                CommonTokens.PopIgnoreWhitespaceControl,
                ")",
            ],
        )

        super(FuncType, self).__init__(
            DynamicPhrasesType.Types,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # '('
                    "(",
                    CommonTokens.PushIgnoreWhitespaceControl,

                    # <attribute>*
                    ZeroOrMorePhraseItem.Create(
                        name="Attributes",
                        item=AttributePhraseItem.Create(),
                    ),

                    # <type>
                    DynamicPhrasesType.Types,

                    # <parameters>
                    type_only_parameters_phrase_item,

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
            assert len(nodes) == 8

            # <attribute>*
            attributes_node = cast(Optional[AST.Node], nodes[2])

            attribute_data: List[List[AttributePhraseItem.AttributeData]] = []

            for attribute_node in cast(List[AST.Node], ExtractRepeat(attributes_node)):
                attribute_data.append(AttributePhraseItem.ExtractLexerData(cast(AST.Node, attribute_node)))

            # TODO: Leverage attribute data
            is_exceptional_node = None
            is_exceptional_info = None

            is_generator_node = None
            is_generator_info = None

            is_reentrant_node = None
            is_reentrant_info = None

            is_scoped_node = None
            is_scoped_info = None

            is_async_node = None
            is_async_info = None

            # <type>
            type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, nodes[3])))
            type_info = cast(TypeParserInfo, GetParserInfo(type_node))

            # <parameters>
            parameters_node = cast(AST.Node, nodes[4])

            parameters_nodes = ExtractSequence(parameters_node)
            assert len(parameters_nodes) == 5

            parameters_nodes = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], parameters_nodes[2])))
            if parameters_nodes is None:
                parameters_info: Union[bool, List[FunctionParameterTypeParserInfo]] = False
            else:
                parameters_nodes = ExtractSequence(parameters_nodes)
                assert len(parameters_nodes) == 3

                parameters_info: Union[bool, List[FunctionParameterTypeParserInfo]] = []

                for parameter_node in itertools.chain(
                    [parameters_nodes[0]],
                    (
                        ExtractSequence(delimited_node)[1]
                        for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, parameters_nodes[1])))
                    ),
                ):
                    parameter_nodes = ExtractSequence(cast(AST.Node, parameter_node))
                    assert len(parameter_nodes) == 2

                    # <type>
                    parameter_type_node = cast(AST.Node, ExtractDynamic(cast(AST.Node, parameter_nodes[0])))
                    parameter_type_info = cast(TypeParserInfo, GetParserInfo(parameter_type_node))

                    # '*'?
                    is_variadic_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], parameter_nodes[1])))
                    if is_variadic_node is None:
                        is_variadic_info = None
                    else:
                        is_variadic_info = True

                    parameters_info.append(
                        FunctionParameterTypeParserInfo(
                            CreateParserRegions(
                                parameter_node,
                                parameter_type_node,
                                is_variadic_node,
                            ),  # type: ignore
                            parameter_type_info,
                            is_variadic_info,
                        ),
                    )

                assert parameters_info

            # <modifier>?
            modifier_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[7])))
            if modifier_node is None:
                modifier_info = None
            else:
                modifier_info = TypeModifier.Extract(modifier_node)

            return FuncTypeParserInfo(
                CreateParserRegions(
                    node,
                    type_node,
                    parameters_node,
                    is_generator_node,
                    is_reentrant_node,
                    is_exceptional_node,
                    is_scoped_node,
                    is_async_node,
                    modifier_node,
                ),  # type: ignore
                type_info,
                parameters_info,
                is_generator_info,
                is_reentrant_info,
                is_exceptional_info,
                is_scoped_info,
                is_async_info,
                modifier_info,
            )

        # ----------------------------------------------------------------------

        return Impl
