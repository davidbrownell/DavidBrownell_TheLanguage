import os

from typing import cast, List, Optional, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens as CommonTokens
    from .Impl import ArgumentsPhraseItemImpl

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

    from ....Parser.Common.TemplateArgumentParserInfo import (
        TemplateArgumentParserInfo,
        TemplateDecoratorExpressionParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    item_phrase_item = PhraseItem.Create(
        name="Argument",
        item=[
            # (<type_name> '=')?
            OptionalPhraseItem.Create(
                name="Keyword",
                item=[
                    CommonTokens.GenericUpperName,
                    "=",
                ],
            ),

            (
                DynamicPhrasesType.TemplateDecoratorExpressions,
                DynamicPhrasesType.Types,
            ),
        ],
    )

    return ArgumentsPhraseItemImpl.Create(
        "Template Arguments",
        "<", ">",
        item_phrase_item,
        allow_empty=False,
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> List[TemplateArgumentParserInfo]:
    return cast(
        List[TemplateArgumentParserInfo],
        ArgumentsPhraseItemImpl.ExtractParserInfo(
            _ExtractTemplateArgumentInfo,
            node,
            allow_empty=False,
        ),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractTemplateArgumentInfo(
    node: Node,
) -> Tuple[ParserInfo, bool]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 2

    # (<type_name> '=')?
    keyword_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[0])))
    if keyword_node is None:
        keyword_info = None
    else:
        keyword_nodes = ExtractSequence(keyword_node)
        assert len(keyword_nodes) == 2

        keyword_node = cast(Leaf, keyword_nodes[0])
        keyword_info = cast(str, ExtractToken(keyword_node))

        if (
            not CommonTokens.TemplateTypeParameterNameRegex.match(keyword_info)
            and not CommonTokens.TemplateDecoratorParameterNameRegex.match(keyword_info)
        ):
            raise CommonTokens.InvalidTokenError.FromNode(keyword_node, keyword_info, "template type or template decorator")

    # (<template_expression>, <type_name>)
    value_node = cast(Node, ExtractOr(cast(Node, nodes[1])))

    if isinstance(value_node, Leaf):
        value_node = cast(Leaf, value_node)
        value_info = cast(str, ExtractToken(value_node))

        if not CommonTokens.TemplateTypeParameterNameRegex.match(value_info):
            raise CommonTokens.InvalidTokenError.FromNode(value_node, value_info, "template type")
    else:
        value_node = cast(Node, ExtractDynamic(value_node))
        value_info = cast(TemplateDecoratorExpressionParserInfo, GetParserInfo(value_node))

    return (
        TemplateArgumentParserInfo(
            CreateParserRegions(node, value_node, keyword_node),  # type: ignore
            value_info,
            keyword_info,
        ),
        keyword_node is not None,
    )
