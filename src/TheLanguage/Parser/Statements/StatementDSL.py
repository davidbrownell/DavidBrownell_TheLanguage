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

    from ..Components.Statement import Statement
    from ..Components.Token import RegexToken, Token


# ----------------------------------------------------------------------
# TODO: Change this name to DynamicStatementType
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
    Types                                   = auto()    # Statements used in types

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

    # Most of the time, this flag does not need to be set. However, setting it to True will prevent
    # infinite recursion errors when the first statement in a sequence is a DynamicStatement that
    # includes the parent.
    #
    # For example, the following statement will suffer from infinite recursion unless this flag is
    # set:
    #
    #   Name:   AsStatement
    #   Type:   DynamicStatements.Expressions
    #   DSL:    [
    #               DynamicStatements.Expressions,
    #               'as'
    #               DynamicStatements.Types,
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

        assert isinstance(first_item, DynamicStatements), first_item

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

    elif isinstance(item.item, DynamicStatements):
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
