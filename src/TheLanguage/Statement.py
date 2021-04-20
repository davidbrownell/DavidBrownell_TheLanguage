# ----------------------------------------------------------------------
# |
# |  Statement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-13 20:54:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Statement-related functionality"""

import os

from typing import List, NamedTuple, Optional, Tuple, Union

import CommonEnvironment
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

from NormalizedIterator import NormalizedIterator
from Token import (
    DedentToken,
    IndentToken,
    NewlineToken,
    PushIgnoreWhitespaceControlToken,
    PopIgnoreWhitespaceControlToken,
    Token,
)

# ----------------------------------------------------------------------
class Statement(Interface.Interface):
    """Abstract base class for objects that identify tokens"""

    # ----------------------------------------------------------------------
    class ParseResultItem(NamedTuple):
        whitespace: Optional[Tuple[int, int]]           # Whitespace immediately before the token
        value: Token.MatchType                          # Result of the call to Token.Match
        iter: NormalizedIterator                        # NormalizedIterator after the token has been consumed
        is_ignored: bool                                # True if the result is whitespace while whitespace is being ignored

    # ----------------------------------------------------------------------
    class ParseResult(NamedTuple):
        success: bool
        results: List["ParseResultItem"]
        iter: NormalizedIterator

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def Name(self):
        """Name of the statement"""
        raise Exception("Abstract property")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Parse(
        normalized_iter: NormalizedIterator,
    ) -> "ParseResult":
        raise Exception("Abstract method")

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
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
class StandardStatement(Statement):
    """Statement type that parses tokens"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        items: List[Union[Statement, Token]],
    ):
        assert name
        assert items

        # Ensure that all control tokens are balanced properly
        control_token_check = {}

        for item_index, item in enumerate(items):
            if isinstance(item, Token) and item.IsControlToken:
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
                    assert isinstance(item, item.OpeningToken.ClosingToken), item

                    key = type(item)

                    assert key in control_token_check, item
                    assert control_token_check[key]

                    control_token_check[key].pop()

                    if not control_token_check[key]:
                        del control_token_check[key]

        assert not control_token_check

        self._name                          = name
        self._items                         = items

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def Name(self):
        return self._name

    @property
    def Items(self):
        return self._items

    # ----------------------------------------------------------------------
    @Interface.override
    def Parse(self, normalized_iter):
        normalized_iter = normalized_iter.Clone()

        results = []
        ignore_whitespace_ctr = 0

        eat_indent_token = IndentToken()
        eat_dedent_token = DedentToken()
        eat_newline_token = NewlineToken()
        eat_last_dedent_line: Optional[int] = None

        # ----------------------------------------------------------------------
        def EatWhitespaceTokens() -> bool:
            nonlocal normalized_iter
            nonlocal eat_last_dedent_line

            if not ignore_whitespace_ctr:
                return False

            result = eat_indent_token.Match(normalized_iter)
            if result:
                assert not isinstance(result, list), result

                results.append(
                    Statement.ParseResultItem(
                        None,
                        result,
                        normalized_iter.Clone(),
                        is_ignored=True,
                    ),
                )

                return True

            # We don't want to match dedents over and over, so
            # capture the line that it was found on.
            if normalized_iter.Line != eat_last_dedent_line:
                result = eat_dedent_token.Match(normalized_iter)
                if result:
                    assert isinstance(result, list), result

                    for res in result:
                        results.append(
                            Statement.ParseResultItem(
                                None,
                                res,
                                normalized_iter.Clone(),
                                is_ignored=True,
                            ),
                        )

                    eat_last_dedent_line = normalized_iter.Line
                    return True

            # A potential newline may have potential whitespace
            potential_iter = normalized_iter.Clone()
            potetnial_whitespace = self._ExtractWhitespace(potential_iter)

            result = eat_newline_token.Match(potential_iter)

            if result:
                assert not isinstance(result, list), result

                results.append(
                    Statement.ParseResultItem(
                        potetnial_whitespace,
                        result,
                        potential_iter.Clone(),
                        is_ignored=True,
                    ),
                )

                normalized_iter = potential_iter

                return True

            return False

        # ----------------------------------------------------------------------

        success = True
        item_index = 0

        while item_index < len(self._items):
            if normalized_iter.AtEnd():
                success = False
                break

            if EatWhitespaceTokens():
                continue

            item = self._items[item_index]

            # Statement
            if isinstance(item, Statement):
                result = item.Parse(normalized_iter)

                # Copy any matching contents, even if the call wasn't successful
                results.append(result.results)

                normalized_iter = result.iter

                if not result.success:
                    success = False
                    break

            # Token
            elif isinstance(item, Token):
                if isinstance(item, PushIgnoreWhitespaceControlToken):
                    ignore_whitespace_ctr += 1

                elif isinstance(item, PopIgnoreWhitespaceControlToken):
                    assert ignore_whitespace_ctr
                    ignore_whitespace_ctr -= 1

                elif item.IsControlToken:
                    # This is a control token that we don't recognize; skip it.
                    pass

                else:
                    # We only want to consume the whitespace if there is a match that follows
                    potential_iter = normalized_iter.Clone()
                    potential_whitespace = self._ExtractWhitespace(potential_iter)

                    result = item.Match(potential_iter)
                    if result is None:
                        success = False
                        break

                    if isinstance(result, list):
                        assert not potential_whitespace

                        for res in result:
                            results.append(
                                Statement.ParseResultItem(
                                    None,
                                    res,
                                    potential_iter.Clone(),
                                    is_ignored=False,
                                ),
                            )
                    else:
                        results.append(
                            Statement.ParseResultItem(
                                potential_whitespace,
                                result,
                                potential_iter.Clone(),
                                is_ignored=False,
                            ),
                        )

                    normalized_iter = potential_iter

            else:
                assert False, item

            item_index += 1

        return Statement.ParseResult(success, results, normalized_iter)
