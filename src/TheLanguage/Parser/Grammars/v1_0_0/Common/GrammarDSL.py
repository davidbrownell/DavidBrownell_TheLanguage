# ----------------------------------------------------------------------
# |
# |  GrammarDSL.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:05:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality used across the grammar definition"""

import os

from typing import cast, Generator, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .GrammarAST import (
        ExtractRepeatedNodes,
    )

    # Convenience imports for other files, please do not remove
    from ....Components.AST import Leaf, Node, RootNode

    from ....Statements.StatementDSL import (
        DynamicStatementsType,
        ExtractValues,
        ExtractValuesResultType,
        IsLeafValue,
        Statement,
        StatementItem,
    )

    # Standard imports
    from . import Tokens as CommonTokens
    from ....Statements import StatementDSL
    from ....Components.Token import Token


# ----------------------------------------------------------------------
def CreateStatement(
    item: StatementItem.ItemType,
    name: str=None,
    suffers_from_infinite_recursion=False,
) -> Statement:
    # Single tokens don't have the opportunity to participate in node validation,
    # as there won't be a corresponding node emitted. In this case, turn the token
    # into a sequence.
    if isinstance(item, Token):
        item = [item]

    return StatementDSL.CreateStatement(
        item=item,
        name=name,
        comment_token=CommonTokens.Comment,
        suffers_from_infinite_recursion=suffers_from_infinite_recursion,
    )


# ----------------------------------------------------------------------
def CreateDelimitedStatementItem(
    item: StatementItem.ItemType,
    delimiter_item: StatementItem.ItemType=CommonTokens.Comma,
    are_multiple_items_required=False,
    name: Optional[str]=None,
) -> StatementItem:
    """Creates a list of statements that represent a delimited set of items"""

    return StatementItem(
        name=name or "Delimited Elements",
        item=[
            item,
            StatementItem(
                name="Delimiter and Element",
                item=[
                    delimiter_item,
                    item,
                ],
                arity="+" if are_multiple_items_required else "*",
            ),
            StatementItem(
                name="Trailing Delimiter",
                item=delimiter_item,
                arity="?",
            ),
        ],
    )


# ----------------------------------------------------------------------
# BugBug: Remove this when it is no longer being used
def ExtractDelimitedNodes(
    node: Node,
) -> Generator[Node, None, None]:
    # <item>
    assert len(node.Children) >= 1
    yield cast(Node, node.Children[0])

    # (<delimiter> <item>)+|*
    potential_items = ExtractRepeatedNodes(node, 1, "Delimiter and Element")
    for child in (potential_items or []):
        # Leaf nodes can be children if the caller is ignoring whitespace; skip them here.
        if not isinstance(child, Node):
            continue

        assert len(child.Children) >= 2, child
        yield cast(Node, child.Children[-1])


# ----------------------------------------------------------------------
# BugBug: Remove this when it is no longer being used
from ....Statements.StatementDSL import NodeInfo

def ExtractDelimitedNodeInfo(
    node_info: NodeInfo.AnyType,
) -> Generator[NodeInfo.AnyType, None, None]:
    # <item>
    yield node_info[0]  # type: ignore

    # (<delimiter> <item>){+|*}
    if NodeInfo.IsRepeat(node_info[1]):  # type: ignore
        for result in node_info[1]:  # type: ignore
            yield result[1]


# ----------------------------------------------------------------------
def ExtractDelimitedNodeValues(
    values: ExtractValuesResultType,
) -> Generator[ExtractValuesResultType, None, None]:

    # <item>
    yield values[0]  # type: ignore

    # (<delimiter> <item>){+|*}
    for value in values[1]:  # type: ignore
        yield value[1]
