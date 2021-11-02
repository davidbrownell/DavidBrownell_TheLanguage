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
        ExtractOr,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        OptionalPhraseItem,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo
    from ....Parser.ParserInfo import ParserInfo

    from ....Parser.Common.TemplateParametersParserInfo import (
        TemplateDecoratorExpressionParserInfo,
        TemplateDecoratorParameterParserInfo,
        TemplateDecoratorTypeParserInfo,
        TemplateParametersParserInfo,
        TemplateTypeParameterParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    item_phrase_item = PhraseItem.Create(
        name="Parameter",
        item=(
            # <type_name> ('=' <type>)
            PhraseItem.Create(
                name="Type",
                item=[
                    CommonTokens.GenericUpperName,

                    OptionalPhraseItem.Create(
                        name="With Default",
                        item=[
                            "=",
                            CommonTokens.GenericUpperName,
                        ],
                    ),
                ],
            ),

            # <decorator_type> <decorator_name> ('=' <decorator_expression>)
            PhraseItem.Create(
                name="Decorator",
                item=[
                    DynamicPhrasesType.TemplateDecoratorTypes,
                    CommonTokens.GenericUpperName,

                    OptionalPhraseItem.Create(
                        name="With Default",
                        item=[
                            "=",
                            DynamicPhrasesType.TemplateDecoratorExpressions,
                        ],
                    ),
                ],
            ),
        ),
    )

    return ParametersPhraseItemImpl.Create(
        "Template Parameters",
        "<", ">",
        item_phrase_item,
        allow_empty=False,
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> TemplateParametersParserInfo:
    result = ParametersPhraseItemImpl.ExtractParserInfo(
        TemplateParametersParserInfo,
        _ExtractTemplateParameterInfo,
        node,
        allow_empty=False,
    )

    assert isinstance(result, TemplateParametersParserInfo)
    return result


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractTemplateParameterInfo(
    node: Node,
) -> Tuple[ParserInfo, bool]:
    node = cast(Node, ExtractOr(node))

    assert node.Type is not None

    if node.Type.Name == "Type":
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        # <type_name>
        type_name_node = cast(Leaf, nodes[0])
        type_name_info = cast(str, ExtractToken(type_name_node))

        if not CommonTokens.TemplateTypeParameterNameRegex.match(type_name_info):
            raise CommonTokens.InvalidTokenError.FromNode(type_name_node, type_name_info, "template type")

        # TODO: Is var args
        is_var_args_node = None
        is_var_args_info = None

        # ('=' <type_name>)
        default_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[1])))
        if default_node is None:
            default_info = None
        else:
            default_nodes = ExtractSequence(default_node)
            assert len(default_nodes) == 2

            default_leaf = cast(Leaf, default_nodes[1])
            default_info = cast(str, ExtractToken(default_leaf))

            if not CommonTokens.TemplateTypeParameterNameRegex.match(default_info):
                raise CommonTokens.InvalidTokenError.FromNode(default_leaf, default_info, "template type")

        return (
            TemplateTypeParameterParserInfo(
                CreateParserRegions(node, type_name_node, default_leaf, is_var_args_node),  # type: ignore
                type_name_info,
                default_info,
                is_var_args_info,
            ),
            default_info is not None,
        )

    elif node.Type.Name == "Decorator":
        nodes = ExtractSequence(node)
        assert len(nodes) == 3

        # <template_type>
        template_type_node = cast(Node, ExtractDynamic(cast(Node, nodes[0])))
        template_type_info = cast(TemplateDecoratorTypeParserInfo, GetParserInfo(template_type_node))

        # <name>
        name_node = cast(Leaf, nodes[1])
        name_info = cast(str, ExtractToken(name_node))

        if not CommonTokens.TemplateDecoratorParameterNameRegex.match(name_info):
            raise CommonTokens.InvalidTokenError.FromNode(name_node, name_info, "template decorator type")

        # ('=' <template_expression>)
        default_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
        if default_node is None:
            default_info = None
        else:
            default_nodes = ExtractSequence(default_node)
            assert len(default_nodes) == 2

            default_node = cast(Node, ExtractDynamic(cast(Node, default_nodes[1])))
            default_info = cast(TemplateDecoratorExpressionParserInfo, GetParserInfo(default_node))

        return (
            TemplateDecoratorParameterParserInfo(
                CreateParserRegions(node, name_node, template_type_node, default_node),  # type: ignore
                name_info,
                template_type_info,
                default_info,
            ),
            default_info is not None,
        )

    else:
        assert False, node.Type  # pragma: no cover
