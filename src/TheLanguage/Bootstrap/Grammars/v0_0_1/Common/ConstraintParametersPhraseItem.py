import os

from typing import cast, Optional, Tuple

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

    from ....Parser.Common.ConstraintParametersParserInfo import (
        ConstraintParameterParserInfo,
        ConstraintParametersParserInfo,
        TemplateDecoratorExpressionParserInfo,
        TemplateDecoratorTypeParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    # <decorator_type> <decorator_name> ('=' <decorator_expression>)?
    item_phrase_item = PhraseItem.Create(
        name="Parameter",
        item=[
            DynamicPhrasesType.TemplateDecoratorTypes,
            CommonTokens.GenericLowerName,

            OptionalPhraseItem.Create(
                name="With Default",
                item=[
                    "=",
                    DynamicPhrasesType.TemplateDecoratorExpressions,
                ],
            ),
        ],
    )

    return ParametersPhraseItemImpl.Create(
        "Constraint Parameters",
        "{", "}",
        item_phrase_item,
        allow_empty=False,
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> ConstraintParametersParserInfo:
    result = ParametersPhraseItemImpl.ExtractParserInfo(
        ConstraintParametersParserInfo,
        _ExtractConstraintParserInfo,
        node,
        allow_empty=False,
    )

    assert isinstance(result, ConstraintParametersParserInfo)
    return result


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractConstraintParserInfo(
    node: Node,
) -> Tuple[ParserInfo, bool]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 3

    # <decorator_type>
    type_node = cast(Node, ExtractDynamic(cast(Node, nodes[0])))
    type_info = cast(TemplateDecoratorTypeParserInfo, GetParserInfo(type_node))

    # <decorator_name>
    name_leaf = cast(Leaf, nodes[1])
    name_info = cast(str, ExtractToken(name_leaf))

    if not CommonTokens.ConstraintParameterNameRegex.match(name_info):
        raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "constraint type")

    # ('=' <decorator_expression>)?
    default_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
    if default_node is None:
        default_info = None
    else:
        default_nodes = ExtractSequence(default_node)
        assert len(default_nodes) == 2

        default_node = cast(Node, ExtractDynamic(cast(Node, default_nodes[1])))
        default_info = cast(TemplateDecoratorExpressionParserInfo, GetParserInfo(default_node))

    return (
        ConstraintParameterParserInfo(
            CreateParserRegions(node, type_node, name_leaf, default_node),  # type: ignore
            type_info,
            name_info,
            default_info,
        ),
        default_info is not None,
    )
