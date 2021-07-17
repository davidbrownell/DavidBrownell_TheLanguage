# ----------------------------------------------------------------------
# |
# |  SequenceStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-12 08:58:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the SequenceStatement object"""

import os

from typing import cast, Iterable, List, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Statement import Statement
    from .RecursivePlaceholderStatement import RecursivePlaceholderStatement
    from .TokenStatement import TokenStatement

    from ..Token import (
        ControlTokenBase,
        DedentToken,
        IndentToken,
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
class SequenceStatement(Statement):
    """Matches a sequence of statements"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        comment_token: RegexToken,
        *statements: Statement,
        name: str=None,
        unique_id: Optional[List[str]]=None,
        type_id: Optional[int]=None,
        _name_is_default: Optional[bool]=None,
    ):
        assert comment_token
        assert statements
        assert all(statement for statement in statements)

        # Ensure that any control token requiring a pair has a peer
        control_token_tracker = set()

        for statement in statements:
            if isinstance(statement, TokenStatement) and statement.Token.IsControlToken:
                control_token = cast(ControlTokenBase, statement.Token)

                if control_token.ClosingToken is not None:
                    key = type(control_token)
                    if key in control_token_tracker:
                        assert False, key

                    control_token_tracker.add(key)

                if control_token.OpeningToken is not None:
                    key = control_token.OpeningToken

                    if key not in control_token_tracker:
                        assert False, key

                    control_token_tracker.remove(key)

        assert not control_token_tracker, control_token_tracker

        # Initialize the class
        if name is None:
            name = self._CreateDefaultName(statements)
            _name_is_default = True
        elif _name_is_default is None:
            _name_is_default = False

        super(SequenceStatement, self).__init__(
            name,
            unique_id=unique_id,
            type_id=type_id,
        )

        cloned_statements = [
            statement.Clone(
                unique_id=self.UniqueId + ["Sequence: {} [{}]".format(statement.Name, statement_index)],
            )
            for statement_index, statement in enumerate(statements)
        ]

        self.CommentToken                   = comment_token
        self.Statements                     = cloned_statements
        self._original_statements           = statements
        self._name_is_default               = _name_is_default

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        unique_id: List[str],
    ) -> Statement:
        return self.CloneImpl(
            self.CommentToken,
            *self._original_statements,
            name=self.Name,
            unique_id=unique_id,
            type_id=self.TypeId,
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
        success = True

        observer.StartStatement([self])
        with CallOnExit(lambda: observer.EndStatement([(self, success)])):
            original_normalized_iter = normalized_iter.Clone()

            ignore_whitespace_ctr = 1 if ignore_whitespace else 0

            # ----------------------------------------------------------------------
            def ExtractWhitespaceOrComments() -> Optional[
                Tuple[
                    List[Statement.TokenParseResultData],
                    Statement.NormalizedIterator,
                ]
            ]:
                if ignore_whitespace_ctr:
                    data_item = self._ExtractPotentialWhitespaceToken(normalized_iter)
                    if data_item is not None:
                        return [data_item], data_item.IterAfter

                return self._ExtractPotentialCommentTokens(normalized_iter)

            # ----------------------------------------------------------------------

            data_items: List[Optional[Statement.ParseResultData]] = []

            observer_decorator = Statement.ObserverDecorator(
                self,
                observer,
                data_items,
                lambda data_item: data_item,
            )

            for statement in self.Statements:
                # Extract whitespace or comments
                while not normalized_iter.AtEnd():
                    potential_prefix_info = ExtractWhitespaceOrComments()
                    if potential_prefix_info is None:
                        break

                    data_items += potential_prefix_info[0]
                    normalized_iter = potential_prefix_info[1]

                # Process control tokens
                if isinstance(statement, TokenStatement) and statement.Token.IsControlToken:
                    if isinstance(statement.Token, PushIgnoreWhitespaceControlToken):
                        ignore_whitespace_ctr += 1
                    elif isinstance(statement.Token, PopIgnoreWhitespaceControlToken):
                        assert ignore_whitespace_ctr != 0
                        ignore_whitespace_ctr -= 1
                    else:
                        assert False, statement.Token  # pragma: no cover

                    continue

                if normalized_iter.AtEnd():
                    success = False
                    break

                # Process the statement
                result = await statement.ParseAsync(
                    normalized_iter.Clone(),
                    observer_decorator,
                    ignore_whitespace=ignore_whitespace_ctr != 0,
                    single_threaded=single_threaded,
                )

                if result is None:
                    return None

                # Preserve the results
                if result.Data:
                    data_items.append(result.Data)

                normalized_iter = result.Iter.Clone()

                if not result.Success:
                    success = False
                    break

            data = Statement.StandardParseResultData(
                self,
                Statement.MultipleStandardParseResultData(data_items, True),
            )

            if (
                success
                and not await observer.OnInternalStatementAsync(
                    [data],
                    original_normalized_iter,
                    normalized_iter,
                )
            ):
                return None

            return Statement.ParseResult(success, normalized_iter, data)

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
    @classmethod
    def _ExtractPotentialWhitespaceToken(
        cls,
        normalized_iter: Statement.NormalizedIterator,
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
    def _ExtractPotentialCommentTokens(
        self,
        normalized_iter: Statement.NormalizedIterator,
    ) -> Optional[
        Tuple[
            List[Statement.TokenParseResultData],
            Statement.NormalizedIterator,
        ]
    ]:
        """Eats any comment (stand-alone or trailing) when requested"""

        normalized_iter = normalized_iter.Clone()

        at_beginning_of_line = normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart

        if at_beginning_of_line and normalized_iter.LineInfo.HasNewIndent():
            normalized_iter_begin = normalized_iter.Clone()
            normalized_iter.SkipPrefix()

            potential_whitespace = normalized_iter_begin.Offset, normalized_iter.Offset
        else:
            potential_whitespace = TokenStatement.ExtractWhitespace(normalized_iter)

        normalized_iter_begin = normalized_iter.Clone()

        result = self.CommentToken.Match(normalized_iter)
        if result is None:
            return None

        results = [
            Statement.TokenParseResultData(
                self.CommentToken,
                potential_whitespace,
                result,
                normalized_iter_begin,
                normalized_iter,
                IsIgnored=True,
            ),
        ]

        # Add additional content if we are at the beginning of the line
        if at_beginning_of_line:
            # Capture the trailing newline
            result = self._ExtractPotentialWhitespaceToken(results[-1].IterAfter)
            assert result

            results.append(result)

            # Consume the dedent, but don't return it with the results (as we absorbed the
            # corresponding indent when we skipped the prefix above)
            if results[0].Whitespace is not None:
                result = self._ExtractPotentialWhitespaceToken(results[-1].IterAfter)
                assert result

                return results, result.IterAfter

        return results, results[-1].IterAfter

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def PopulateRecursiveImpl(
        self,
        new_statement: Statement,
    ) -> bool:
        updated_statements = False

        for statement_index, statement in enumerate(self.Statements):
            if isinstance(statement, RecursivePlaceholderStatement):
                self.Statements[statement_index] = new_statement
                updated_statements = True
            else:
                updated_statements = statement.PopulateRecursiveImpl(new_statement) or updated_statements

        if updated_statements and self._name_is_default:
            self.Name = self._CreateDefaultName(self.Statements)

        return updated_statements

    # ----------------------------------------------------------------------
    @staticmethod
    def _CreateDefaultName(
        statements: Iterable[Statement],
    ) -> str:
        return "Sequence: [{}]".format(", ".join([statement.Name for statement in statements]))
