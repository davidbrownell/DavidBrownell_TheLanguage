# ----------------------------------------------------------------------
# |
# |  AttributesPhraseItem.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 08:17:05
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used when lexing attributes"""

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
    from . import ArgumentsPhraseItem
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
    Arguments: Optional[Union[bool, List[ArgumentsPhraseItem.ArgumentParserInfo]]]
    ArgumentsNode: Optional[Node]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert (
            (self.Arguments is None and self.ArgumentsNode is None)
            or (self.Arguments is not None and self.ArgumentsNode is not None)
        )


# ----------------------------------------------------------------------
def Create(
    allow_multiple=True,

) -> Union[ZeroOrMorePhraseItem, OptionalPhraseItem]:
    """\
    ('@' <generic_name> <<Arguments>>? <newline>?)*
        - or -
    ('@' <generic_name> <<Arguments>>? <newline>?)?             # If 'allow_multiple' is False
    """

    phrase_item = PhraseItem.Create(
        name="Attribute",
        item=[
            "@",
            CommonTokens.GenericUpperName,
            OptionalPhraseItem(ArgumentsPhraseItem.Create()),
            OptionalPhraseItem(CommonTokens.Newline),
        ],
    )

    if allow_multiple:
        return ZeroOrMorePhraseItem.Create(
            name="Attributes",
            item=phrase_item,
        )

    return OptionalPhraseItem(phrase_item)


# ----------------------------------------------------------------------
def ExtractLexerData(
    node: Optional[Node],
) -> List[AttributeData]:
    if node is None:
        return []

    node_or_nodes = ExtractRepeat(node)

    if not isinstance(node_or_nodes, list):
        node_or_nodes = [node_or_nodes]

    results: List[AttributeData] = []

    for node in cast(List[Node], node_or_nodes):
        nodes = ExtractSequence(node)
        assert len(nodes) == 4

        # <generic_name>
        name_leaf = cast(Leaf, nodes[1])
        name_info = cast(str, ExtractToken(name_leaf))

        if not CommonTokens.AttributeNameRegex.match(name_info):
            raise CommonTokens.InvalidTokenError.FromNode(name_leaf, name_info, "attribute")

        # <<Arguments>>?
        arguments_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[2])))
        if arguments_node is None:
            arguments_info = None
        else:
            arguments_info = ArgumentsPhraseItem.ExtractParserInfo(arguments_node)

        results.append(AttributeData(name_info, name_leaf, arguments_info, arguments_node))

    return results
