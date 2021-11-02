import os

from typing import cast, List, Optional, Tuple

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
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        OptionalPhraseItem,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo
    from ....Parser.ParserInfo import ParserInfo

    from ....Parser.Common.ConstraintArgumentParserInfo import (
        ConstraintArgumentParserInfo,
        TemplateDecoratorExpressionParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    item_phrase_item = PhraseItem.Create(
        name="Argument",
        item=[
            # (<constraint_name> '=')?
            OptionalPhraseItem.Create(
                name="Keyword",
                item=[
                    CommonTokens.GenericLowerName,
                    "=",
                ],
            ),

            DynamicPhrasesType.TemplateDecoratorExpressions,
        ],
    )

    return ArgumentsPhraseItemImpl.Create(
        "Constraint Arguments",
        "{", "}",
        item_phrase_item,
        allow_empty=False,
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> List[ConstraintArgumentParserInfo]:
    return cast(
        List[ConstraintArgumentParserInfo],
        ArgumentsPhraseItemImpl.ExtractParserInfo(
            _ExtractConstraintArgumentInfo,
            node,
            allow_empty=False,
        ),
    )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractConstraintArgumentInfo(
    node: Node,
) -> Tuple[ParserInfo, bool]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 2

    # (<constraint_name> '=')?
    keyword_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[0])))
    if keyword_node is None:
        keyword_info = None
    else:
        keyword_nodes = ExtractSequence(keyword_node)
        assert len(keyword_nodes) == 2

        keyword_node = cast(Leaf, keyword_nodes[0])
        keyword_info = cast(str, ExtractToken(keyword_node))

        if not CommonTokens.ConstraintParameterNameRegex.match(keyword_info):
            raise CommonTokens.InvalidTokenError.FromNode(keyword_node, keyword_info, "constraint parameter")

    # <template_decorator_expression>
    expression_node = cast(Node, ExtractDynamic(cast(Node, nodes[1])))
    expression_info = cast(TemplateDecoratorExpressionParserInfo, GetParserInfo(expression_node))

    return (
        ConstraintArgumentParserInfo(
            CreateParserRegions(node, expression_node, keyword_node),  # type: ignore
            expression_info,
            keyword_info,
        ),
        keyword_node is not None,
    )
