# ----------------------------------------------------------------------
# |
# |  AttributesPhraseItem.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-06 11:34:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality that helps when working with attributes"""

import os

from typing import Any, cast, List, Optional, Tuple

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
        PhraseItem,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class AttributeData(object):
    Name: str
    NameLeaf: Leaf
    Arguments: Optional[List[ArgumentsPhraseItem.ArgumentParserInfo]]
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
) -> PhraseItem:
    """\
    ('@' <name> <<Arguments>>? <newline>?)*
        - or -
    ('@' <name> <<Arguments>>? <newline>?)?    # If allow_multiple is False
    """

    return PhraseItem(
        name="Attribute",
        item=[
            "@",
            CommonTokens.MethodName,
            PhraseItem(
                item=ArgumentsPhraseItem.Create(),
                arity="?",
            ),

            PhraseItem(
                item=CommonTokens.Newline,
                arity="?",
            ),
        ],
        arity="*" if allow_multiple else "?",
    )


# ----------------------------------------------------------------------
def ExtractData(
    node: Optional[Node],
) -> List[AttributeData]:
    if node is None:
        return []

    node_or_nodes = ExtractRepeat(node)

    if isinstance(node_or_nodes, list):
        return [_ExtractAttribute(cast(Node, child)) for child in node_or_nodes]

    return [_ExtractAttribute(cast(Node, node_or_nodes))]


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractAttribute(
    node: Node,
) -> AttributeData:
    nodes = ExtractSequence(node)
    assert len(nodes) == 4

    # <name>
    leaf = cast(Leaf, nodes[1])
    name = cast(str, ExtractToken(leaf))

    # <<Arguments>>?
    arguments_node = cast(Optional[Node], ExtractOptional(cast(Node, nodes[2])))
    if arguments_node is not None:
        arguments_info = ArgumentsPhraseItem.ExtractParserInfo(cast(Node, arguments_node))
    else:
        arguments_info = None

    return AttributeData(name, leaf, arguments_info, arguments_node)
