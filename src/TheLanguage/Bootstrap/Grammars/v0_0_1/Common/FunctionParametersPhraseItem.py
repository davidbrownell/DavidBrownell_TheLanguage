import os

from typing import cast, Optional, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens
    from .Impl import ParametersPhraseItemImpl

    from ....Lexer.Phrases.DSL import (
        DynamicPhrasesType,
        ExtractDynamic,
        ExtractOptional,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        OptionalPhraseItem,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo
    from ....Parser.ParserInfo import ParserInfo

    from ....Parser.Common.FunctionParametersParserInfo import (
        ExpressionParserInfo,
        FunctionParameterParserInfo,
        FunctionParametersParserInfo,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    item_phrase_item = PhraseItem.Create(
        name="Parameter",
        item=[
            # <type>
            DynamicPhrasesType.Types,

            # '*'?
            OptionalPhraseItem.Create(
                name="Variadic",
                item="*",
            ),

            # <generic_name>
            CommonTokens.GenericLowerName,

            # ('=' <expression>)?
            OptionalPhraseItem.Create(
                name="With Default",
                item=[
                    "=",
                    DynamicPhrasesType.Expressions,
                ],
            ),
        ],
    )

    return ParametersPhraseItemImpl.Create(
        "Function Parameters",
        "(", ")",
        item_phrase_item,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> Union[bool, FunctionParametersParserInfo]:
    return ParametersPhraseItemImpl.ExtractParserInfo(
        FunctionParametersParserInfo,
        _ExtractFunctionParserInfo,
        node,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractFunctionParserInfo(
    node: Node,
) -> Tuple[ParserInfo, bool]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 4

    # <type>
    type_node = cast(Node, ExtractDynamic(cast(Node, nodes[0])))
    type_info = cast(TypeParserInfo, GetParserInfo(type_node))

    # '*'?
    is_variadic_node = cast(Optional[Node], ExtractOptional(cast(Node, nodes[1])))
    if is_variadic_node is None:
        is_variadic_info = None
    else:
        is_variadic_info = True

    # <generic_name>
    name_leaf = cast(Leaf, nodes[2])
    name_info = cast(str, ExtractToken(name_leaf))

    if not CommonTokens.ParameterNameRegex.match(name_info):
        raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "parameter")

    # ('=' <expression>)?
    default_node = cast(Optional[Node], ExtractOptional(cast(Node, nodes[3])))
    if default_node is None:
        default_info = None
    else:
        default_nodes = ExtractSequence(default_node)
        assert len(default_nodes) == 2

        default_node = cast(Node, ExtractDynamic(cast(Node, default_nodes[1])))
        default_info = cast(ExpressionParserInfo, GetParserInfo(default_node))

    return (
        FunctionParameterParserInfo(
            CreateParserRegions(node, type_node, is_variadic_node, name_leaf, default_node),  # type: ignore
            type_info,
            is_variadic_info,
            name_info,
            default_info,
        ),
        default_info is not None,
    )
