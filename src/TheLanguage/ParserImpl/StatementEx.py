# ----------------------------------------------------------------------
# |
# |  StatementEx.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-26 08:33:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StatementEx object"""

import os
import re
import textwrap

from enum import auto, Enum
from typing import cast, List, Optional, Set, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator

    from .StatementImpl.DynamicStatement import DynamicStatement
    from .StatementImpl.OrStatement import OrStatement
    from .StatementImpl.RepeatStatement import RepeatStatement
    from .StatementImpl.Statement import Statement
    from .StatementImpl.TokenStatement import TokenStatement

    from .Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
        Token as TokenClass,
    )


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
class StatementEx(Statement):
    """Executes the given statements sequentially"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    ItemType                                = Union[
        Statement,
        TokenClass,
        DynamicStatements,
        List["StatementEx.ItemType"],                                       # Or
        Tuple["StatementEx.ItemType", int, Optional[int]],                  # Repeat: (Type, Min, Max)
        None,                                                               # Item to be populated later
        "StatementEx.NamedItem",
    ]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class NamedItem(object):
        """Wrapper that can be used to provide a name of the statement rather than using the default"""

        Name: str
        Item: "StatementEx.ItemType"

    # ----------------------------------------------------------------------
    # Note that defining this value here within a Statement isn't ideal,
    # as it represents the first instantiation of a grammar-specific rule
    # at this level (outside of whitespace as a specifier of lexical scope).
    # However, the alternative is that either every statement is instantiated
    # with a comment token (which will always be the same for a grammar), or
    # we introduce functionality to dynamically create Statement-like classes
    # (with embedded knowledge of what a comment looks like) and then use
    # that class to instantiate Statement objects. None of these approaches
    # are ideal.

    CommentToken                            = RegexToken(
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
    class Observer(Statement.Observer):
        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def GetDynamicStatements(
            value: DynamicStatements,
        ) -> Union[
            Tuple[str, List[Statement]],
            List[Statement],
        ]:
            """Returns all currently available dynamic statements based on the current scope"""
            raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    ParseResult                             = Statement.ParseResult
    ParseResultData                         = Statement.ParseResultData

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        *items: "StatementEx.ItemType",
        populate_empty=False,
    ):
        super(StatementEx, self).__init__(name)

        self._items: List[StatementEx.ItemType]                             = list(items)
        self.Statements: Optional[List[Statement]]                          = None

        self._PopulateStatements(
            self if populate_empty else None,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    async def ParseAsync(
        self,
        normalized_iter: Statement.NormalizedIterator,
        observer: Statement.Observer,
        ignore_whitespace=False,
        single_threaded=False,
    ) -> Union[
        Statement.ParseResult,
        None,
    ]:
        if self.Statements is None:
            raise Exception("The statement has not been populated by an upstream statement")

        normalized_iter = normalized_iter.Clone()

        ignore_whitespace_ctr = 1 if ignore_whitespace else 0
        success = True
        data_items = []

        # ----------------------------------------------------------------------
        def ExtractWhitespaceOrComments() -> Optional[Statement.TokenParseResultData]:
            nonlocal success

            if ignore_whitespace_ctr:
                data_item = self._ExtractPotentialWhitespaceToken(normalized_iter)
                if data_item is not None:
                    return data_item

            data_item = self._ExtractPotentialInlineCommentToken(normalized_iter)
            if data_item is not None:
                return data_item

            return None

        # ----------------------------------------------------------------------

        queue_command_observer = Statement.QueueCommandObserver(observer)

        for statement_index, statement in enumerate(self.Statements):
            # Extract whitespace or comments
            while not normalized_iter.AtEnd():
                potential_data_item = ExtractWhitespaceOrComments()
                if potential_data_item is None:
                    break

                data_items.append(potential_data_item)
                normalized_iter = potential_data_item.IterAfter.Clone()

            # Process control tokens
            if isinstance(statement, TokenStatement) and statement.Token.IsControlToken:
                if isinstance(statement.Token, PushIgnoreWhitespaceControlToken):
                    ignore_whitespace_ctr += 1
                elif isinstance(statement.Token, PopIgnoreWhitespaceControlToken):
                    assert ignore_whitespace_ctr != 0
                    ignore_whitespace_ctr -= 1

                    if statement_index == len(self.Statements) - 1:
                        break
                else:
                    assert False, statement.Token  # pragma: no cover

                continue

            if normalized_iter.AtEnd():
                success = False
                break

            # Process the statement
            result = await statement.ParseAsync(
                normalized_iter.Clone(),
                queue_command_observer,
                ignore_whitespace=ignore_whitespace_ctr != 0,
                single_threaded=single_threaded,
            )

            assert result is not None

            # Notify the observer
            if (
                result.Success
                and not isinstance(statement, TokenStatement)
            ):
                on_internal_statement_result = queue_command_observer.OnInternalStatement(
                    statement,
                    result.Data,
                    normalized_iter,
                    result.Iter,
                )

                assert on_internal_statement_result

            # Preserve the results
            data_items.append(Statement.StandardParseResultData(statement, result.Data))
            normalized_iter = result.Iter

            if not result.Success:
                success = False
                break

        if success and not queue_command_observer.Replay():
            return None

        if len(self._items) == 1 and len(data_items) == 1:
            return Statement.ParseResult(
                success,
                normalized_iter,
                data_items[0],
            )

        return Statement.ParseResult(
            success,
            normalized_iter,
            Statement.MultipleStandardParseResultData(data_items),
        )

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _indent_token                           = IndentToken()
    _dedent_token                           = DedentToken()
    _newline_token                          = NewlineToken()

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    def _PopulateStatements(
        self,
        populate_statement: Optional[Statement],
    ):
        if self.Statements is None:
            statements: List[Statement] = []

            for item in self._items:
                item_statement = self._PopulateStatementItem(item, populate_statement)
                if item_statement is None:
                    return None

                statements.append(item_statement)

            self.Statements = statements

        return self

    # ----------------------------------------------------------------------
    @classmethod
    def _PopulateStatementItem(
        cls,
        item: "StatementEx.ItemType",
        populate_statement: Optional[Statement],
        name: Optional[str]=None,
    ) -> Optional[Statement]:
        if isinstance(item, StatementEx):
            assert name is None, name
            return item._PopulateStatements(populate_statement)

        elif isinstance(item, Statement):
            assert name is None, name
            return item

        elif isinstance(item, TokenClass):
            assert name is None, name
            return TokenStatement(item)

        elif isinstance(item, DynamicStatements):
            return DynamicStatement(
                lambda observer: observer.GetDynamicStatements(item),
                name=name or str(item),
            )

        elif isinstance(item, list):
            orStatements: List[Statement] = []

            for i in item:
                this_statement = cls._PopulateStatementItem(i, populate_statement)
                if this_statement is None:
                    return None

                orStatements.append(this_statement)

            return OrStatement(
                *orStatements,
                name=name,
            )

        elif isinstance(item, tuple):
            repeat_statement, min_matches, max_matches = item

            repeat_statement = cls._PopulateStatementItem(repeat_statement, populate_statement)
            if repeat_statement is None:
                return None

            return RepeatStatement(
                repeat_statement,
                min_matches,
                max_matches,
                name=name,
            )

        elif item is None:
            assert name is None, name
            return populate_statement

        elif isinstance(item, StatementEx.NamedItem):
            return cls._PopulateStatementItem(
                item.Item,
                populate_statement,
                name=item.Name,
            )

        else:
            assert False, item  # pragma: no cover

    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractPotentialWhitespaceToken(
        cls,
        normalized_iter: NormalizedIterator,
    ) -> Optional[Statement.TokenParseResultData]:
        """Eats any whitespace token when requested"""

        normalized_iter_begin = normalized_iter.Clone()
        normalized_iter = normalized_iter.Clone()

        # Potential indent or dedent
        for token in [
            cls._indent_token,
            cls._dedent_token,
        ]:
            result = token.Match(normalized_iter)
            if result is not None:
                return Statement.TokenParseResultData(
                    token,
                    None,
                    result,
                    normalized_iter_begin,
                    normalized_iter,
                    IsIgnored=True,
                )

        # A potential newline
        potential_whitespace = TokenStatement.ExtractWhitespace(normalized_iter)
        normalized_iter_begin = normalized_iter.Clone()

        result = cls._newline_token.Match(normalized_iter)
        if result is not None:
            return Statement.TokenParseResultData(
                cls._newline_token,
                potential_whitespace,
                result,
                normalized_iter_begin,
                normalized_iter,
                IsIgnored=True,
            )

        return None

    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractPotentialInlineCommentToken(
        cls,
        normalized_iter: NormalizedIterator,
    ) -> Optional[Statement.TokenParseResultData]:
        """Eats any comment when requested"""

        normalized_iter = normalized_iter.Clone()
        potential_whitespace = TokenStatement.ExtractWhitespace(normalized_iter)
        normalized_iter_begin = normalized_iter.Clone()

        result = cls.CommentToken.Match(normalized_iter)
        if result is not None:
            return Statement.TokenParseResultData(
                cls.CommentToken,
                potential_whitespace,
                result,
                normalized_iter_begin,
                normalized_iter,
                IsIgnored=True,
            )

        return None
