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
    from .Token import RegexToken, Token

    from .Statements.DynamicStatement import DynamicStatement
    from .Statements.OrStatement import OrStatement
    from .Statements.RecursivePlaceholderStatement import RecursivePlaceholderStatement
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
                name=name,
            ),
        )
    else:
        statement = _PopulateItem(comment_token, item)

    statement.PopulateRecursive()

    return statement


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
        return RecursivePlaceholderStatement()

    if not isinstance(item, StatementItem):
        item = StatementItem(item)

    name = None

    if isinstance(item.item, Statement):
        statement = item.item
        name = item.name

    elif isinstance(item.item, Token):
        statement = TokenStatement(
            item.item,
            name=item.name,
        )

    elif isinstance(item.item, DynamicStatements):
        dynamic_statement_value = item.item

        # ----------------------------------------------------------------------
        def GetDynamicStatements(
            unique_id: List[str],
            observer,
        ):
            return observer.GetDynamicStatements(unique_id, dynamic_statement_value)

        # ----------------------------------------------------------------------

        statement = DynamicStatement(
            GetDynamicStatements,
            name=item.name or str(item.item),
        )

    elif isinstance(item.item, list):
        statement = SequenceStatement(
            comment_token,
            *[_PopulateItem(comment_token, i) for i in item.item],
            name=item.name,
        )

    elif isinstance(item.item, tuple):
        statement = OrStatement(
            *[_PopulateItem(comment_token, i) for i in item.item],
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
