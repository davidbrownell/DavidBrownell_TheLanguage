import itertools
import os

from typing import cast, List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import FunctionArgumentsPhraseItem
    from . import Tokens as CommonTokens

    from ....Lexer.Phrases.DSL import (
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        OptionalPhraseItem,
        PhraseItem,
        ZeroOrMorePhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class AttributeData(object):
    Name: str
    NameLeaf: Leaf
    Arguments: Optional[Union[bool, List[FunctionArgumentsPhraseItem.FunctionArgumentParserInfo]]]
    ArgumentsNode: Optional[Node]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert (
            (self.Arguments is None and self.ArgumentsNode is None)
            or (self.Arguments is not None and self.ArgumentsNode is not None)
        )


# ----------------------------------------------------------------------
def Create() -> PhraseItem:
    attribute_item = [
        CommonTokens.GenericUpperName,

        OptionalPhraseItem.Create(
            item=FunctionArgumentsPhraseItem.Create(),
        ),
    ]

    return PhraseItem.Create(
        name="Attribute",
        item=[
            # '['
            "[",
            CommonTokens.PushIgnoreWhitespaceControl,

            # <attribute_item> (',' <attribute_item>)* ','?
            attribute_item,

            ZeroOrMorePhraseItem.Create(
                name="Comma and Attribute",
                item=[
                    ",",
                    attribute_item,
                ],
            ),

            OptionalPhraseItem.Create(
                name="Trailing Comma",
                item=",",
            ),

            # ']'
            CommonTokens.PopIgnoreWhitespaceControl,
            "]",

            OptionalPhraseItem.Create(
                item=CommonTokens.Newline,
            ),
        ],
    )


# ----------------------------------------------------------------------
def ExtractLexerData(
    node: Node,
) -> List[AttributeData]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 8

    results: List[AttributeData] = []

    for attribute_node in itertools.chain(
        [nodes[2]],
        (
            ExtractSequence(delimited_node)[1]
            for delimited_node in cast(List[Node], ExtractRepeat(cast(Node, nodes[3])))
        ),
    ):
        attribute_nodes = ExtractSequence(cast(Node, attribute_node))
        assert len(attribute_nodes) == 2

        # <name>
        name_leaf = cast(Leaf, attribute_nodes[0])
        name_info = cast(str, ExtractToken(name_leaf))

        if not CommonTokens.AttributeNameRegex.match(name_info):
            raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "attribute")

        # <arguments>?
        arguments_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], attribute_nodes[1])))
        if arguments_node is None:
            arguments_info = None
        else:
            arguments_info = FunctionArgumentsPhraseItem.ExtractParserInfo(arguments_node)

        results.append(AttributeData(name_info, name_leaf, arguments_info, arguments_node))

    assert results
    return results
