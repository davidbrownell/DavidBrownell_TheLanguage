# ----------------------------------------------------------------------
# |
# |  Statement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-27 22:06:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Statement object"""

import os
import textwrap

from concurrent.futures import Future
from enum import auto, Enum
from typing import Any, cast, Callable, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import StringHelpers

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NormalizedIterator import NormalizedIterator

    from .Token import (
        ControlTokenBase,
        DedentToken,
        IndentToken,
        NewlineToken,
        PushIgnoreWhitespaceControlToken,
        PopIgnoreWhitespaceControlToken,
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
class Statement(object):
    """Statement made of of Tokens, nested Statements, requests for Dynamic Statements, etc."""

    # ----------------------------------------------------------------------
    # |
    # |  Incoming Types (types used when calling methods within the class)
    # |
    # ----------------------------------------------------------------------
    ItemType                                = Union[
        TokenClass,
        "Statement",
        DynamicStatements,
        List["ItemType"],                   # Or
        Tuple["ItemType", int, int],        # Repeat: (Type, Min, Max)
    ]

    # ----------------------------------------------------------------------
    class Observer(Interface.Interface):
        """Observes events generated by calls to Parse"""

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def Enqueue(
            funcs: List[Callable[[], None]],
        ) -> List[Future]:
            """Enqueues the funcs for execution"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def GetDynamicStatements(
            value: DynamicStatements,
        ) -> List["Statement"]:
            """Returns all currently available dynamic statements based on the current scope"""
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def OnIndent(
            statement: "Statement",
            results: "Statement.ParseResultItemsType",
        ):
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def OnDedent(
            statement: "Statement",
            results: "Statement.ParseResultItemsType",
        ):
            raise Exception("Abstract method")  # pragma: no cover

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.abstractmethod
        def OnInternalStatement(
            result: "Statement.StatementParseResultItem",
            iter_before: NormalizedIterator,
            iter_after: NormalizedIterator,
        ) -> bool:                          # True to continue, False to terminate
            """Invoked when an internal statement is successfully matched"""
            raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Outgoing Types (types generated as output from methods within the class)
    # |
    # ----------------------------------------------------------------------
    ParseResultItemType                     = Union[
        "Statement.TokenParseResultItem",
        "Statement.StatementParseResultItem",
    ]

    ParseResultItemsType                    = List[ParseResultItemType]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class TokenParseResultItem(object):
        Token: TokenClass

        Whitespace: Optional[Tuple[int, int]]           # Whitespace immediately before the token
        Value: TokenClass.MatchType                     # Result of the call to Token.Match
        Iter: NormalizedIterator                        # NormalizedIterator after the token has been consumed
        IsIgnored: bool                                 # True if the result is whitespace while whitespace is being ignored

        # ----------------------------------------------------------------------
        def __str__(self) -> str:
            return "{typ} <<{value}>> ws:{ws}{ignored} [{line}, {column}]".format(
                typ=Statement.ItemTypeToString(self.Token),
                value=str(self.Value),
                ws="None" if self.Whitespace is None else "({}, {})".format(self.Whitespace[0], self.Whitespace[1]),
                ignored=" !Ignored!" if self.IsIgnored else "",
                line=self.Iter.Line,
                column=self.Iter.Column,
            )


    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class StatementParseResultItem(object):
        Statement: Union["Statement", DynamicStatements]
        Results: "Statement.ParseResultItemsType"

        # ----------------------------------------------------------------------
        def __str__(self) -> str:
            results = [str(result).rstrip() for result in self.Results]
            if not results:
                results.append("<No results>")

            return textwrap.dedent(
                """\
                {name}
                    {results}
                """,
            ).format(
                name=Statement.ItemTypeToString(self.Statement),
                results=StringHelpers.LeftJustify(
                    "\n".join(results),
                    4,
                ).rstrip(),
            )

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ParseResult(object):
        Success: bool
        Results: "Statement.ParseResultItemsType"
        Iter: NormalizedIterator

        # ----------------------------------------------------------------------
        def __str__(self) -> str:
            results = [str(result).rstrip() for result in self.Results]
            if not results:
                results.append("<No results>")

            return textwrap.dedent(
                """\
                {success}
                {iter}
                    {results}
                """,
            ).format(
                success=self.Success,
                iter=self.Iter.Offset,
                results=StringHelpers.LeftJustify(
                    "\n".join(results),
                    4,
                ),
            )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        *items: ItemType,
    ):
        assert name
        assert items

        # Validate the incoming items
        control_token_check = {}            # Ensure that all control tokens are balanced properly

        for item_index, item in enumerate(items):
            if isinstance(item, tuple):
                min_matches, max_matches = item[1:]

                assert min_matches >= 0, min_matches
                assert max_matches is None or max_matches >= min_matches, (min_matches, max_matches)

            elif isinstance(item, TokenClass) and item.IsControlToken:
                item = cast(ControlTokenBase, item)

                # Whitespace cannot come before the push token
                if isinstance(item, PushIgnoreWhitespaceControlToken):
                    assert item_index == 0 or not isinstance(items[item_index - 1], (NewlineToken, IndentToken, DedentToken))

                # Whitespace cannot come after the pop token
                if isinstance(item, PopIgnoreWhitespaceControlToken):
                    assert item_index == len(items) - 1 or not isinstance(items[item_index + 1], (NewlineToken, IndentToken, DedentToken))

                # Ensure matching tokens
                if item.ClosingToken is not None:
                    control_token_check.setdefault(item.ClosingToken, []).append(item)
                    continue

                if item.OpeningToken is not None:
                    assert isinstance(item, item.OpeningToken.ClosingToken), item  # type: ignore

                    key = type(item)

                    assert key in control_token_check, item
                    assert control_token_check[key]

                    control_token_check[key].pop()

                    if not control_token_check[key]:
                        del control_token_check[key]

        assert not control_token_check

        self.Name                           = name
        self.Items                          = list(items)

    # ----------------------------------------------------------------------
    def Parse(
        self,
        normalized_iter: NormalizedIterator,
        observer: "Statement.Observer",

        # True to ignore whitespace tokens (the results will still be returned,
        # they will not participate in statement matching)
        ignore_whitespace=False,

        # True to execute all statements within a single thread
        single_threaded=False,
    ) -> Optional["Statement.ParseResult"]:
        """Parses the provided content"""

        parser = self._Parser(
            self,
            normalized_iter.Clone(),
            observer,
            ignore_whitespace=ignore_whitespace,
            single_threaded=single_threaded,
        )

        item_index = 0
        success = True

        while item_index < len(self.Items):
            if parser.normalized_iter.AtEnd():
                success = False
                break

            success = parser.ParseItem(self.Items[item_index])
            if success is None:
                return None

            if not success:
                break

            item_index += 1

        return self.ParseResult(success, parser.results, parser.normalized_iter)

    # ----------------------------------------------------------------------
    @classmethod
    def ParseMultiple(
        cls,
        statements: List["Statement"],
        normalized_iter: NormalizedIterator,
        observer: "Statement.Observer",
        ignore_whitespace=False,

        # True to ensure that results are sorted to find the best possible match
        # (regardless of statement order). False will return the first statement
        # matched.
        sort_results=True,

        # True to execute all statements within a single thread
        single_threaded=False,
    ) -> Optional["Statement.ParseResult"]:
        """Simultaneously applies multiple statements at the provided location"""

        use_futures = not single_threaded and len(statements) != 1

        # ----------------------------------------------------------------------
        def Impl(statement):
            parser = Statement._Parser(
                statement,
                normalized_iter.Clone(),
                observer,
                ignore_whitespace=ignore_whitespace,
                single_threaded=single_threaded,
            )

            success = parser.ParseItem(statement)
            if success is None:
                return None

            return Statement.ParseResult(success, parser.results, parser.normalized_iter)

        # ----------------------------------------------------------------------

        if use_futures:
            futures = observer.Enqueue(
                [
                    lambda statement=statement: Impl(statement)
                    for statement in statements
                ],
            )

            results = []

            for future in futures:
                result = future.result()
                if result is None:
                    return None

                results.append(result)

        else:
            results = []

            for statement in statements:
                result = Impl(statement)
                if result is None:
                    return None

                results.append(result)

        if sort_results:
            # Stable sort according to the criteria:
            #   - Success
            #   - Longest matched content

            sort_data = [
                (
                    index,
                    1 if result.Success else 0,
                    result.Iter.Offset,
                )
                for index, result in enumerate(results)
            ]

            sort_data.sort(
                key=lambda value: value[1:],
                reverse=True,
            )

            result = results[sort_data[0][0]]

        else:
            result = None

            for potential_result in results:
                if potential_result.Success:
                    result = potential_result

                    break

            if result is None:
                result = results[0]

        if result.Success:
            return Statement.ParseResult(
                True,
                [
                    Statement.StatementParseResultItem(
                        statements,
                        result.Results,
                    ),
                ],
                result.Iter,
            )

        return_results: Statement.ParseResultItemsType = []
        max_iter: Optional[NormalizedIterator] = None

        for result in results:
            return_results += result.Results

            if max_iter is None or result.Iter.Offset > max_iter.Offset:
                max_iter = result.Iter

        return Statement.ParseResult(
            False,
            [
                Statement.StatementParseResultItem(
                    statements,
                    return_results,
                ),
            ],
            cast(NormalizedIterator, max_iter),
        )

    # ----------------------------------------------------------------------
    @classmethod
    def ItemTypeToString(
        cls,
        item: "Statement.ItemType",
    ) -> str:
        if isinstance(item, TokenClass):
            return item.Name
        elif isinstance(item, cls):
            return item.Name
        elif isinstance(item, DynamicStatements):
            return str(item)
        elif isinstance(item, list):
            return "Or: [{}]".format(", ".join([cls.ItemTypeToString(value) for value in item]))
        elif isinstance(item, tuple):
            statement, min_matches, max_matches = item

            return "Repeat: ({}, {}, {})".format(
                cls.ItemTypeToString(statement),
                min_matches,
                max_matches,
            )
        else:
            assert False, item  # pragma: no cover

        # Make the linter happy
        return ""  # pragma: no cover

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    class _Parser(object):
        """Maintains state information between calls to ParseItem"""

        # ----------------------------------------------------------------------
        def __init__(
            self,
            statement: "Statement",
            normalized_iter: NormalizedIterator,
            observer: "Statement.Observer",
            ignore_whitespace: bool,
            single_threaded: bool,
        ):
            self._statement                 = statement
            self._observer                  = observer
            self._ignore_whitespace_ctr     = 1 if ignore_whitespace else 0
            self._single_threaded           = single_threaded

            self.normalized_iter            = normalized_iter
            self.results                    = []

        # ----------------------------------------------------------------------
        def ParseItem(
            self,
            item: "Statement.ItemType",
        ) -> Optional[bool]:
            """Parses an individual item"""

            if self._ignore_whitespace_ctr:
                while True:
                    whitespace_results = self._EatWhitespaceToken(self.normalized_iter)
                    if whitespace_results is None:
                        break

                    self.results += whitespace_results
                    self.normalized_iter = self.results[-1].Iter.Clone()

            # Token
            if isinstance(item, TokenClass):
                if isinstance(item, PushIgnoreWhitespaceControlToken):
                    self._ignore_whitespace_ctr += 1

                elif isinstance(item, PopIgnoreWhitespaceControlToken):
                    assert self._ignore_whitespace_ctr
                    self._ignore_whitespace_ctr -= 1

                elif item.IsControlToken:
                    # This is a control token that we don't recognize; skip it
                    pass

                else:
                    # We only want to consume whitespace if there is a match that follows it
                    potential_iter = self.normalized_iter.Clone()
                    potential_whitespace = self._ExtractWhitespace(potential_iter)

                    result = item.Match(potential_iter)
                    if result is None:
                        return False

                    if isinstance(item, IndentToken):
                        self._observer.OnIndent(self._statement, self.results)
                    elif isinstance(item, DedentToken):
                        self._observer.OnDedent(self._statement, self.results)

                    if isinstance(result, list):
                        assert not potential_whitespace

                        self.results += [
                            Statement.TokenParseResultItem(
                                item,
                                potential_whitespace,
                                res,
                                potential_iter.Clone(),
                                IsIgnored=False,
                            )
                            for res in result
                        ]
                    else:
                        self.results.append(
                            Statement.TokenParseResultItem(
                                item,
                                potential_whitespace,
                                result,
                                potential_iter.Clone(),
                                IsIgnored=False,
                            ),
                        )

                    self.normalized_iter = potential_iter

                return True

            # Statements
            statement_parse_result_item = None

            if isinstance(item, DynamicStatements):
                result = Statement.ParseMultiple(
                    self._observer.GetDynamicStatements(item),
                    self.normalized_iter,
                    self._observer,
                    ignore_whitespace=self._ignore_whitespace_ctr != 0,
                    single_threaded=self._single_threaded,
                )

            elif isinstance(item, Statement):
                result = item.Parse(
                    self.normalized_iter,
                    self._observer,
                    ignore_whitespace=self._ignore_whitespace_ctr != 0,
                    single_threaded=self._single_threaded,
                )

                if (
                    result is not None
                    and result.Success
                    and not self._observer.OnInternalStatement(
                        Statement.StatementParseResultItem(
                            item,
                            result.Results,
                        ),
                        self.normalized_iter,
                        result.Iter,
                    )
                ):
                    return None

            elif isinstance(item, tuple):
                statement, min_matches, max_matches = item

                result = self._ParseRepeat(
                    statement,
                    self.normalized_iter,
                    self._observer,
                    min_matches,
                    max_matches,
                    ignore_whitespace=self._ignore_whitespace_ctr != 0,
                    single_threaded=self._single_threaded,
                )

                if (
                    result is not None
                    and result.Success
                ):
                    for repeated_result in result.Results:
                        if not self._observer.OnInternalStatement(
                            repeated_result,
                            self.normalized_iter,
                            result.Iter
                        ):
                            return None

            elif isinstance(item, list):
                result = Statement.ParseMultiple(
                    item,
                    self.normalized_iter,
                    self._observer,
                    ignore_whitespace=self._ignore_whitespace_ctr != 0,
                    single_threaded=self._single_threaded,
                    sort_results=False,
                )

                statement_parse_result_item = result.Results[0]
                assert isinstance(statement_parse_result_item, Statement.StatementParseResultItem)

                if (
                    result is not None
                    and result.Success
                ):
                    assert len(result.Results) == 1

                    if not self._observer.OnInternalStatement(
                        statement_parse_result_item,
                        self.normalized_iter,
                        result.Iter,
                    ):
                        return None

            else:
                assert False, item  # pragma: no cover

            if result is None:
                return None

            if statement_parse_result_item is None:
                statement_parse_result_item = Statement.StatementParseResultItem(
                    item,
                    result.Results,
                )

            self.results.append(statement_parse_result_item)
            self.normalized_iter = result.Iter.Clone()

            return result.Success

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        _indent_token                           = IndentToken()
        _dedent_token                           = DedentToken()
        _newline_token                          = NewlineToken()

        # ----------------------------------------------------------------------
        @classmethod
        def _EatWhitespaceToken(
            cls,
            normalized_iter: NormalizedIterator,
        ) -> Optional[List["Statement.TokenParseResultItem"]]:
            """Eats any whitespace token when requested"""

            normalized_iter = normalized_iter.Clone()

            result = cls._indent_token.Match(normalized_iter)
            if result is not None:
                assert not isinstance(result, list), result

                return [
                    Statement.TokenParseResultItem(
                        cls._indent_token,
                        None,
                        result,
                        normalized_iter,
                        IsIgnored=True,
                    ),
                ]

            result = cls._dedent_token.Match(normalized_iter)
            if result is not None:
                assert isinstance(result, list), result

                return [
                    Statement.TokenParseResultItem(
                        cls._dedent_token,
                        None,
                        res,
                        normalized_iter.Clone(),
                        IsIgnored=True,
                    )
                    for res in result
                ]

            # A potential newline may have potential whitespace
            potential_iter = normalized_iter.Clone()
            potential_whitespace = cls._ExtractWhitespace(potential_iter)

            result = cls._newline_token.Match(potential_iter)
            if result is not None:
                assert not isinstance(result, list), result

                return [
                    Statement.TokenParseResultItem(
                        cls._newline_token,
                        potential_whitespace,
                        result,
                        potential_iter,
                        IsIgnored=True,
                    ),
                ]

            return None

        # ----------------------------------------------------------------------
        @staticmethod
        def _ExtractWhitespace(
            normalized_iter: NormalizedIterator,
        ) -> Optional[Tuple[int, int]]:
            """Consumes any whitespace located at the current offset"""

            if normalized_iter.Offset == normalized_iter.LineInfo.OffsetStart:
                if (
                    not normalized_iter.LineInfo.HasNewIndent()
                    and not normalized_iter.LineInfo.HasNewDedents()
                ):
                    normalized_iter.SkipPrefix()

            else:
                start = normalized_iter.Offset

                while (
                    normalized_iter.Offset < normalized_iter.LineInfo.OffsetEnd
                    and normalized_iter.Content[normalized_iter.Offset].isspace()
                    and normalized_iter.Content[normalized_iter.Offset] != "\n"
                ):
                    normalized_iter.Advance(1)

                if normalized_iter.Offset != start:
                    return start, normalized_iter.Offset

            return None

        # ----------------------------------------------------------------------
        @staticmethod
        def _ParseRepeat(
            statement: "Statement",
            normalized_iter: NormalizedIterator,
            observer: "Statement.Observer",
            min_matches: int,
            max_matches: int,
            ignore_whitespace=False,
            single_threaded=False,
        ) -> Optional["Statement.ParseResult"]:
            """Matches N times"""

            assert min_matches >= 0, min_matches
            assert max_matches is None or max_matches >= min_matches, (min_matches, max_matches)

            results: List[Statement.StatementParseResultItem] = []

            while True:
                result = statement.Parse(
                    normalized_iter,
                    observer,
                    ignore_whitespace=ignore_whitespace,
                    single_threaded=single_threaded,
                )
                if not result.Success:
                    break

                results.append(
                    Statement.StatementParseResultItem(statement, result.Results),
                )

                normalized_iter = result.Iter.Clone()

                if max_matches is not None and len(results) == max_matches:
                    break

            if min_matches == 0 and max_matches == 1:
                success = len(results) <= 1
            else:
                success = (
                    len(results) >= min_matches
                    and (
                        max_matches is None
                        or len(results) == max_matches
                    )
                )

            return Statement.ParseResult(
                success,
                cast(Statement.ParseResultItemsType, results),
                normalized_iter,
            )
