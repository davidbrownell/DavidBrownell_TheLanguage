# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:59:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains utilities used by multiple statements and expressions"""

import os

from typing import cast, List, Match, Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...GrammarStatement import (
        Leaf,
        Node,
        RootNode,
        Statement,
    )

    from ....Components.Token import Token

    from ....Statements.DynamicStatement import DynamicStatement
    from ....Statements.OrStatement import OrStatement
    from ....Statements.RepeatStatement import RepeatStatement


# ----------------------------------------------------------------------
def ExtractLeafValue(
    leaf: Leaf,
    group_value_name: Optional[str]="value",
) -> str:
    result = cast(
        Token.RegexMatch,
        leaf.Value,
    ).Match

    if group_value_name is not None:
        result = result.group(group_value_name)
    else:
        result = result.string[result.start() : result.end()]

    return result


# ----------------------------------------------------------------------
def ExtractDynamicExpressionNode(
    node: Node,
) -> Node:
    # Drill into the Dynamic Expression node
    assert isinstance(node.Type, DynamicStatement)
    assert len(node.Children) == 1
    node = cast(Node, node.Children[0])

    # Drill into the grammar node
    assert isinstance(node.Type, OrStatement)
    assert len(node.Children) == 1
    node = cast(Node, node.Children[0])

    return node


# ----------------------------------------------------------------------
def ExtractOptionalNode(
    parent: Node,
    child_index: int,
    name: Optional[str]=None,
) -> Optional[Union[Leaf, Node]]:
    children = ExtractRepeatedNodes(
        parent,
        child_index=child_index,
        name=name,
    )

    if children is None:
        return None

    assert len(children) == 1
    return children[0]


# ----------------------------------------------------------------------
def ExtractRepeatedNodes(
    parent: Node,
    child_index: Optional[int]=None,
    name: Optional[str]=None,
) -> Optional[List[Union[Leaf, Node]]]:
    if child_index is None:
        node = parent
    else:
        if len(parent.Children) <= child_index:
            return None

        node = parent.Children[child_index]

    if not isinstance(node.Type, RepeatStatement):
        return None

    statement = cast(RepeatStatement, node.Type)

    if name and statement.Statement.Name != name:
        return None

    node = cast(Node, node)

    return node.Children


# ----------------------------------------------------------------------
def ExtractOrNode(
    node: Node,
) -> Union[Leaf, Node]:
    assert isinstance(node.Type, OrStatement)
    assert len(node.Children) == 1
    return node.Children[0]
