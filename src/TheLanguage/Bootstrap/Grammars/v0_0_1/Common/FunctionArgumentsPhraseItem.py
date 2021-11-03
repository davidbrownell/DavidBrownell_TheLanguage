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
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        OptionalPhraseItem,
        PhraseItem,
    )

    from ....Parser.Parser import CreateParserRegions, GetParserInfo
    from ....Parser.ParserInfo import ParserInfo

    from ....Parser.Common.FunctionArgumentParserInfo import (
        ExpressionParserInfo,
        FunctionArgumentParserInfo,
    )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    item_phrase_item = PhraseItem.Create(
        name="Argument",
        item=[
            # (<parameter_name> '=')?
            OptionalPhraseItem.Create(
                name="Keyword",
                item=[
                    CommonTokens.GenericLowerName,
                    "=",
                ],
            ),

            DynamicPhrasesType.Expressions,
        ],
    )

    return ArgumentsPhraseItemImpl.Create(
        "Function Arguments",
        "(", ")",
        item_phrase_item,
        allow_empty=True,
    )


# ----------------------------------------------------------------------
def ExtractParserInfo(
    node: Node,
) -> Union[bool, List[FunctionArgumentParserInfo]]:
    results = ArgumentsPhraseItemImpl.ExtractParserInfo(
        _ExtractFunctionArgumentInfo,
        node,
        allow_empty=True,
    )

    if not results:
        return False

    return cast(List[FunctionArgumentParserInfo], results)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractFunctionArgumentInfo(
    node: Node,
) -> Tuple[ParserInfo, bool]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 2

    # (<parameter_name> '=')?
    keyword_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[0])))
    if keyword_node is None:
        keyword_info = None
    else:
        keyword_nodes = ExtractSequence(keyword_node)
        assert len(keyword_nodes) == 2

        keyword_node = cast(Leaf, keyword_nodes[0])
        keyword_info = cast(str, ExtractToken(keyword_node))

        if not CommonTokens.ParameterNameRegex.match(keyword_info):
            raise CommonTokens.InvalidTokenError.FromNode(keyword_node, keyword_info, "parameter")

    # <expression>
    expression_node = cast(Node, ExtractDynamic(cast(Node, nodes[1])))
    expression_info = cast(ExpressionParserInfo, GetParserInfo(expression_node))

    return (
        FunctionArgumentParserInfo(
            CreateParserRegions(node, expression_node, keyword_node),  # type: ignore
            expression_info,
            keyword_info,
        ),
        keyword_node is not None,
    )
