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

from typing import cast, Callable, Generator, List, Optional, Tuple

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    # Convenience imports for other files, please do not remove
    from ....ParserImpl.AST import Leaf, Node, RootNode
    from ....ParserImpl.StatementDSL import (
        DynamicStatements,
        Statement,
        StatementItem,
    )

    # Standard imports
    from . import Tokens as CommonTokens
    from ....ParserImpl import StatementDSL
    from ....ParserImpl.Token import Token
    from ....ParserImpl.Statements.RepeatStatement import RepeatStatement


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
def ExtractDelimitedNodes(
    node: Node,
) -> Generator[Node, None, None]:
    assert len(node.Children) >= 1
    yield cast(Node, node.Children[0])

    if (
        len(node.Children) >= 2
        and isinstance(node.Children[1].Type, RepeatStatement)
        and node.Children[1].Type.Statement.Name == "Delimiter and Element"
    ):
        for child in cast(Node, node.Children[1]).Children:
            # Leaf nodes can be children if the caller is ignoring whitespace; skip them here.
            if not isinstance(child, Node):
                continue

            assert len(child.Children) >= 2, child
            yield cast(Node, child.Children[-1])
