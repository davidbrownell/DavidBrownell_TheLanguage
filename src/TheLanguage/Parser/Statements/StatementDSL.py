# ----------------------------------------------------------------------
# |
# |  StatementDSL.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-12 16:25:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that provides a simple Domain Specific Language (DSL) for creating statements"""

import os
import re
import textwrap

from enum import auto, Enum
from typing import cast, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .DynamicStatement import DynamicStatement
    from .OrStatement import OrStatement
    from .RecursivePlaceholderStatement import RecursivePlaceholderStatement
    from .RepeatStatement import RepeatStatement
    from .SequenceStatement import SequenceStatement
    from .TokenStatement import TokenStatement

    from ..Components.AST import Leaf, Node
    from ..Components.Statement import Statement
    from ..Components.Token import RegexToken, Token


# ----------------------------------------------------------------------
class DynamicStatementsType(Enum):
    """\
    Value that can be used in statements as a placeholder that will be populated dynamically at runtime with statements of the corresponding type.

    Example:
        [
            some_keyword_token,
            newline_token,
            indent_token,
            DynamicStatementsType.Statements,
            dedent_token,
        ]
    """

    Statements                              = auto()    # Statements that do not generate a result
    Expressions                             = auto()    # Statements that generate a result
    Types                                   = auto()    # Statements used in types


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementItem(object):
    ItemType                                = Union[
        "StatementItem",
        Statement,
        Token,
        DynamicStatementsType,
        List["ItemType"],                   # Converts to an SequenceStatement
        Tuple["ItemType", ...],             # Converts to an OrStatement
        None,                               # Populated at a later time
    ]

    # Note that these attributes are named using camel casing so that they match the parameters
    # in CreateStatement.
    item: ItemType
    name: Optional[str]                     = field(default_factory=lambda: None)
    arity: Union[
        str,                                # Valid values are "?", "*", "+"
        Tuple[int, Optional[int]],
    ]                                       = field(default_factory=lambda: (1, 1))

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if isinstance(self.arity, str):
            if self.arity == "?":
                value = (0, 1)
            elif self.arity == "*":
                value = (0, None)
            elif self.arity == "+":
                value = (1, None)
            else:
                raise Exception("'{}' is an invalid arity value".format(self.arity))

            object.__setattr__(self, "arity", value)


# ----------------------------------------------------------------------
CommentToken                                = RegexToken(
    "Comment",
    re.compile(
        textwrap.dedent(
            r"""(?P<value>(?#
                Prefix                  )\#(?#
                Content                 )[^\n]*(?#
            ))""",
        ),
    ),
    is_always_ignored=True,
)


# ----------------------------------------------------------------------
def CreateStatement(
    item: StatementItem.ItemType,
    name: str=None,
    comment_token: RegexToken=None,

    # Most of the time, this flag does not need to be set. However, setting it to True will prevent
    # infinite recursion errors when the first statement in a sequence is a DynamicStatement that
    # includes the parent.
    #
    # For example, the following statement will suffer from infinite recursion unless this flag is
    # set:
    #
    #   Name:   AsStatement
    #   Type:   DynamicStatementsType.Expressions
    #   DSL:    [
    #               DynamicStatementsType.Expressions,
    #               'as'
    #               DynamicStatementsType.Types,
    #           ]
    #
    suffers_from_infinite_recursion=False,
) -> Statement:

    if comment_token is None:
        comment_token = CommentToken

    if suffers_from_infinite_recursion:
        # If this is set, we should be looking at a sequence where the first item is a
        # dynamic expression
        if isinstance(item, list):
            first_item = item[0]

        elif isinstance(item, StatementItem):
            assert isinstance(item.item, list)
            first_item = item.item[0]

        else:
            assert False, item  # pragma: no cover

        assert isinstance(first_item, DynamicStatementsType), first_item

        suffers_from_infinite_recursion_ctr = 1
    else:
        suffers_from_infinite_recursion_ctr = None

    if name is not None:
        assert item is not None
        assert not isinstance(item, StatementItem), item

        statement = _PopulateItem(
            comment_token,
            StatementItem(
                item,
                name=name,
            ),
            suffers_from_infinite_recursion_ctr,
        )
    else:
        statement = _PopulateItem(
            comment_token,
            item,
            suffers_from_infinite_recursion_ctr,
        )

    statement.PopulateRecursive()

    return statement


# ----------------------------------------------------------------------
ExtractValuesResultType                     = Union[
    Tuple[str, Leaf],
    Node,
    List["ExtractValuesResultType"],
    None,
]


# ----------------------------------------------------------------------
def IsLeafValue(
    value: ExtractValuesResultType,
) -> bool:
    return isinstance(value, tuple) and isinstance(value[0], str)


# ----------------------------------------------------------------------
def ExtractValues(
    node: Union[Leaf, Node],
) -> ExtractValuesResultType:
    """Extract values from a node for easier processing."""

    if not isinstance(node, Leaf):
        if isinstance(node.Type, DynamicStatement):
            # Drill into the Dynamic node
            assert len(node.Children) == 1
            node = cast(Node, node.Children[0])

            # Drill into the Or node
            assert isinstance(node.Type, OrStatement)
            assert len(node.Children) == 1
            node = node.Children[0]

        elif isinstance(node.Type, OrStatement):
            # Drill into the Or node
            assert len(node.Children) == 1
            node = node.Children[0]

        elif isinstance(node.Type, RepeatStatement):
            results = []

            for child in node.Children:
                results.append(ExtractValues(child))

            if node.Type.MaxMatches == 1:
                assert results or node.Type.MinMatches == 0, node.Type.MinMatches
                return results[0] if results else None

            return results

        elif isinstance(node.Type, SequenceStatement):
            results = []
            child_index = 0

            while child_index != len(node.Children) or len(results) != len(node.Type.Statements):
                statement = None

                if len(results) != len(node.Type.Statements):
                    statement = node.Type.Statements[len(results)]

                    if isinstance(statement, TokenStatement) and statement.Token.IsControlToken:
                        results.append(None)
                        continue

                child = None

                if child_index != len(node.Children):
                    child = node.Children[child_index]
                    child_index += 1

                    if isinstance(child, Leaf) and child.IsIgnored:
                        continue

                else:
                    assert isinstance(statement, RepeatStatement), statement

                    assert statement.MinMatches == 0, statement.MinMatches
                    results.append(None if statement.MaxMatches == 1 else [])

                    continue

                assert child
                assert statement

                if isinstance(statement, RepeatStatement) and child.Type != statement:
                    assert child_index != 0
                    child_index -= 1

                    assert statement.MinMatches == 0, statement.MinMatches
                    results.append(None if statement.MaxMatches == 1 else [])

                    continue

                results.append(ExtractValues(child))

            assert len(results) == len(node.Type.Statements), (len(results), len(node.Type.Statements))

            return results

        else:
            assert False, node.Type  # pragma: no cover

    if isinstance(node, Leaf):
        result = None

        if isinstance(node.Value, Token.RegexMatch):
            groups_dict = node.Value.Match.groupdict()

            if len(groups_dict) == 1:
                result = next(iter(groups_dict.values()))

        if result is None:
            result = cast(Token, node.Type).Name

        return result, node

    return node


# ----------------------------------------------------------------------
# |
# |  Private Methods
# |
# ----------------------------------------------------------------------
def _PopulateItem(
    comment_token: RegexToken,
    item: StatementItem.ItemType,
    suffers_from_infinite_recursion_ctr: Optional[int],
) -> Statement:
    if item is None:
        return RecursivePlaceholderStatement()

    if not isinstance(item, StatementItem):
        item = StatementItem(item)

    name = None

    if isinstance(item.item, StatementItem):
        statement = _PopulateItem(comment_token, item.item, suffers_from_infinite_recursion_ctr)
        name = item.name

    elif isinstance(item.item, Statement):
        statement = item.item
        name = item.name

    elif isinstance(item.item, Token):
        statement = TokenStatement(
            item.item,
            name=item.name,
        )

    elif isinstance(item.item, DynamicStatementsType):
        dynamic_statement_value = item.item

        if suffers_from_infinite_recursion_ctr == 0:
            # ----------------------------------------------------------------------
            def GetDynamicStatementsWithFilter(
                unique_id: List[str],
                observer,
            ):
                if unique_id[-1] in unique_id[:-1]:
                    return []

                return observer.GetDynamicStatements(unique_id, dynamic_statement_value)

            # ----------------------------------------------------------------------

            get_dynamic_statements_func = GetDynamicStatementsWithFilter

        else:
            # ----------------------------------------------------------------------
            def GetDynamicStatements(
                unique_id: List[str],
                observer,
            ):
                return observer.GetDynamicStatements(unique_id, dynamic_statement_value)

            # ----------------------------------------------------------------------

            get_dynamic_statements_func = GetDynamicStatements

        statement = DynamicStatement(
            get_dynamic_statements_func,
            name=item.name or str(item.item),
        )

    elif isinstance(item.item, list):
        statement = SequenceStatement(
            comment_token,
            *[
                _PopulateItem(
                    comment_token,
                    i,
                    None if suffers_from_infinite_recursion_ctr is None else suffers_from_infinite_recursion_ctr - 1,
                )
                for i in item.item
            ],
            name=item.name,
        )

    elif isinstance(item.item, tuple):
        statement = OrStatement(
            *[
                _PopulateItem(
                    comment_token,
                    i,
                    None if suffers_from_infinite_recursion_ctr is None else suffers_from_infinite_recursion_ctr - 1,
                )
                for i in item.item
            ],
            name=item.name,
        )

    elif item.item is None:
        statement = RecursivePlaceholderStatement()
        name = item.name

    else:
        assert False, item.item  # pragma: no cover

    assert isinstance(item.arity, tuple), item.arity

    if item.arity[0] == 1 and item.arity[1] == 1:
        return statement

    return RepeatStatement(
        statement,
        item.arity[0],
        item.arity[1],
        name=name,
    )
