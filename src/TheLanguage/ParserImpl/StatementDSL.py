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
from typing import Any, List, Optional, Tuple, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Token import RegexToken, Token

    from .Statements.DynamicStatement import DynamicStatement
    from .Statements.OrStatement import OrStatement
    from .Statements.RepeatStatement import RepeatStatement
    from .Statements.SequenceStatement import SequenceStatement
    from .Statements.Statement import Statement
    from .Statements.TokenStatement import TokenStatement


# ----------------------------------------------------------------------
class DynamicStatements(Enum):
    """\
    Value that can be used in statements as a placeholder that will be populated dynamically at runtime with statements of the corresponding type.

    Example:
        [
            some_keyword_token,
            newline_token,
            indent_token,
            DynamicStatements.Statements,
            dedent_token,
        ]
    """

    Statements                              = auto()    # Statements that do not generate a result
    Expressions                             = auto()    # Statements that generate a result


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class StatementItem(object):
    ItemType                                = Union[
        "StatementItem",
        Statement,
        Token,
        DynamicStatements,
        List["ItemType"],                   # Converts to an SequenceStatement
        Tuple["ItemType"],                  # Converts to an OrStatement
        None,                               # Populated at a later time
    ]

    Item: ItemType
    Name: Optional[str]                     = field(default_factory=lambda: None)
    Arity: Union[
        str,                                # Valid values are "?", "*", "+"
        Tuple[int, Optional[int]],
    ]                                       = field(default_factory=lambda: (1, 1))

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if isinstance(self.Arity, str):
            if self.Arity == "?":
                value = (0, 1)
            elif self.Arity == "*":
                value = (0, None)
            elif self.Arity == "+":
                value = (1, None)
            else:
                raise Exception("'{}' is an invalid arity value".format(self.Arity))

            object.__setattr__(self, "Arity", value)


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
) -> Statement:

    if comment_token is None:
        comment_token = CommentToken

    if name is not None:
        assert item is not None
        assert not isinstance(item, StatementItem), item

        statement = _PopulateItem(
            comment_token,
            StatementItem(
                item,
                Name=name,
            ),
        )
    else:
        statement = _PopulateItem(comment_token, item)

    statement.PopulateRecursive(
        statement,
        _PlaceholderStatement,
    )

    return statement


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _PlaceholderStatement(Statement):
    """Statement that should be replaced during final initialization"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        unique_id: Optional[List[str]]=None,
        type_id: Optional[int]=None,
    ):
        super(_PlaceholderStatement, self).__init__("Placeholder")

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        unique_id: List[str],
    ) -> Statement:
        return self.__class__(
            unique_id=unique_id,
            type_id=self.TypeId,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def PopulateRecursive(
        self,
        new_statement: Statement,
        type_to_replace: Any,
    ):
        raise Exception("'PopulateRecursive' should never be called on a _PlaceholderStatement instance")

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(self, *args, **kwargs):
        raise Exception("'ParseAsync' should never be called on a _PlaceholderStatement instance")


# ----------------------------------------------------------------------
# |
# |  Private Methods
# |
# ----------------------------------------------------------------------
def _PopulateItem(
    comment_token: RegexToken,
    item: StatementItem.ItemType,
) -> Statement:
    if item is None:
        return _PlaceholderStatement()

    if not isinstance(item, StatementItem):
        item = StatementItem(item)

    name = None

    if isinstance(item.Item, Statement):
        statement = item.Item
        name = item.Name

    elif isinstance(item.Item, Token):
        statement = TokenStatement(
            item.Item,
            name=item.Name,
        )

    elif isinstance(item.Item, DynamicStatements):
        dynamic_statement_value = item.Item

        # ----------------------------------------------------------------------
        def GetDynamicStatements(
            unique_id: List[str],
            observer,
        ):
            return observer.GetDynamicStatements(unique_id, dynamic_statement_value)

        # ----------------------------------------------------------------------

        statement = DynamicStatement(
            GetDynamicStatements,
            name=item.Name or str(item.Item),
        )

    elif isinstance(item.Item, list):
        statement = SequenceStatement(
            comment_token,
            *[_PopulateItem(comment_token, i) for i in item.Item],
            name=item.Name,
        )

    elif isinstance(item.Item, tuple):
        statement = OrStatement(
            *[_PopulateItem(comment_token, i) for i in item.Item],
            name=item.Name,
        )

    else:
        assert False, item.Item  # pragma: no cover

    assert isinstance(item.Arity, tuple), item.Arity

    if item.Arity[0] == 1 and item.Arity[1] == 1:
        return statement

    return RepeatStatement(
        statement,
        item.Arity[0],
        item.Arity[1],
        name=name,
    )
