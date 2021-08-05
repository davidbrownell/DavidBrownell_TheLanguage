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
from typing import List, Optional, Tuple, Union

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
class NodeInfo(object):
    """Extracts information from a parsed node for easier processing"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class TokenStatementInfo(object):
        Value: Union[str, None]
        Leaf: Leaf

        # ----------------------------------------------------------------------
        def __iter__(self):
            return iter(
                (
                    self.Value,
                    self.Leaf,
                ),
            )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class MissingOptionalStatementInfo(object):
        Statement: Statement

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class SequenceStatementInfo(object):
        Value: List["NodeInfo.AnyType"]
        Statement: Statement

        # ----------------------------------------------------------------------
        def __getitem__(self, key):
            return self.Value[key]

        # ----------------------------------------------------------------------
        def __iter__(self):
            return iter(
                (
                    self.Value,
                    self.Statement,
                ),
            )

    # ----------------------------------------------------------------------
    RepeatStatementInfoType                 = List["NodeInfo.AnyType"]

    # ----------------------------------------------------------------------
    AnyType                                 = Union[
        TokenStatementInfo,
        MissingOptionalStatementInfo,
        SequenceStatementInfo,
        RepeatStatementInfoType,
    ]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def IsToken(
        cls,
        info: "NodeInfo.AnyType",
    ) -> bool:
        return isinstance(info, cls.TokenStatementInfo)

    # ----------------------------------------------------------------------
    @classmethod
    def IsMissing(
        cls,
        info: "NodeInfo.AnyType",
    ) -> bool:
        return isinstance(info, cls.MissingOptionalStatementInfo)

    # ----------------------------------------------------------------------
    @classmethod
    def IsSequence(
        cls,
        info: "NodeInfo.AnyType",
    ) -> bool:
        return isinstance(info, cls.SequenceStatementInfo)

    # ----------------------------------------------------------------------
    @classmethod
    def IsRepeat(
        cls,
        info: "NodeInfo.AnyType",
    ) -> bool:
        return isinstance(info, list)

    # ----------------------------------------------------------------------
    @classmethod
    def Extract(
        cls,
        node: Union[Leaf, Node],
        skip_last_statement=False,
    ) -> "NodeInfo.AnyType":
        assert not skip_last_statement or (
            isinstance(node.Type, SequenceStatement)
            and isinstance(node.Type.Statements[-1], RepeatStatement)
        )

        if isinstance(node.Type, Token):
            assert isinstance(node, Leaf), node

            if node.IsIgnored or not isinstance(node.Value, Token.RegexMatch):
                result = None
            else:
                groups_dict = node.Value.Match.groupdict()
                if len(groups_dict) == 1:
                    result = next(iter(groups_dict.values()))
                else:
                    result = node.Type.Name

            return cls.TokenStatementInfo(result, node)

        assert isinstance(node, Node), node

        if isinstance(node.Type, DynamicStatement):
            # Drill into the dynamic expression
            assert len(node.Children) == 1
            return cls.Extract(node.Children[0])

        elif isinstance(node.Type, OrStatement):
            # Drill into the or node
            assert len(node.Children) == 1
            return cls.Extract(node.Children[0])

        elif isinstance(node.Type, RepeatStatement):
            return [cls.Extract(child) for child in node.Children]

        elif isinstance(node.Type, SequenceStatement):
            results = []

            for child in node.Children:
                if isinstance(child, Leaf) and child.IsIgnored:
                    continue

                statement_index = len(results)
                assert statement_index < len(node.Type.Statements)

                statement = node.Type.Statements[statement_index]

                if (
                    (isinstance(statement, RepeatStatement) and child.Type != statement)
                    or (skip_last_statement and statement_index == len(node.Type.Statements) - 1)
                ):
                    result = None
                else:
                    result = cls.Extract(child)

                    if (
                        isinstance(statement, RepeatStatement)
                        and statement.MaxMatches == 1
                    ):
                        assert isinstance(result, list), result
                        result = result[0] if result else None

                if result is None:
                    results.append(cls.MissingOptionalStatementInfo(statement))
                else:
                    results.append(result)

            return cls.SequenceStatementInfo(results, node.Type)

        assert False, node.Type  # pragma: no cover


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
