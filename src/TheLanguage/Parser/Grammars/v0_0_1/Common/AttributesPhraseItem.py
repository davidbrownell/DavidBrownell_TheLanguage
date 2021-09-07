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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import ArgumentsPhraseItem
    from . import Tokens as CommonTokens

    from ....Phrases.DSL import (
        ExtractOptional,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
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

    if allow_multiple:
        name = "Attributes"
        arity = "*"
    else:
        name = "Attribute"
        arity = "?"

    return PhraseItem(
        name=name,
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
        arity=arity,
    )


# ----------------------------------------------------------------------
def Extract(
    node: Optional[Node],
) -> List[
    Tuple[
        str,                                # Name of function
        Leaf,                               # Leaf associated with name
        Any,                                # Arguments to function
    ]
]:
    if node is None:
        return []

    assert node.Type

    if node.Type.Name == "Attribute":
        return [_ExtractAttribute(node)]

    elif node.Type.Name == "Attributes":
        return [_ExtractAttribute(child) for child in cast(List[Node], ExtractRepeat(node))]

    else:
        assert False, node.Type


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _ExtractAttribute(
    node: Node,
) -> Tuple[str, Leaf, Any]:
    nodes = ExtractSequence(node)
    assert len(nodes) == 4

    # <name>
    leaf = cast(Leaf, nodes[1])
    name = cast(str, ExtractToken(leaf))

    # <<Arguments>>?
    arguments = ExtractOptional(cast(Node, nodes[2]))
    if arguments is not None:
        arguments = ArgumentsPhraseItem.Extract(cast(Node, arguments))

    return name, leaf, arguments