# ----------------------------------------------------------------------
# |
# |  StandardStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-09 08:25:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Standard statement processing"""

import os

from typing import cast, Generator, Iterable, List, Optional, Tuple, Union

from rop import read_only_properties

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Coroutine
    from .NormalizedIterator import NormalizedIterator

    from .Statement import (
        DynamicStatements,
        Statement,
    )

    from .Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        PushIgnoreWhitespaceControlToken,
        PopIgnoreWhitespaceControlToken,
        Token,
    )


# ----------------------------------------------------------------------
@read_only_properties("Items")
class StandardStatement(Statement):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        items: List[
            Union[
                Token,
                Statement,
                DynamicStatements,
                List[Statement],
            ]
        ],
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
        self.Items                          = items

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def Name(self):
        return self._name

    # ----------------------------------------------------------------------
    @Interface.override
    def ParseCoroutine(
        self,
        normalized_iter: NormalizedIterator,
        observer: Statement.Observer,
    ) -> Generator[
        None,
        Coroutine.Status,
        Optional[Statement.ParseResult],
    ]:
        normalized_iter = normalized_iter.Clone()

        results = []
        ignore_whitespace_ctr = 0

        success = True
        item_index = 0

        while item_index < len(self.Items):
            if normalized_iter.AtEnd():
                success = False
                break

            whitespace_results = self._EatWhitespaceToken(ignore_whitespace_ctr, normalized_iter)
            if whitespace_results is not None:
                results += whitespace_results

                normalized_iter = results[-1].Iter.Clone()
                continue

            item = self.Items[item_index]

            # Token
            if isinstance(item, Token):
                if isinstance(item, PushIgnoreWhitespaceControlToken):
                    ignore_whitespace_ctr += 1

                elif isinstance(item, PopIgnoreWhitespaceControlToken):
                    assert ignore_whitespace_ctr
                    ignore_whitespace_ctr -= 1

                elif item.IsControlToken:
                    # This is a control token that we don't recognize; skip it
                    pass

                else:
                    # We only want to consume whitespace if there is a match that follows
                    potential_iter = normalized_iter.Clone()
                    potential_whitespace = self._ExtractWhitespace(potential_iter)

                    result = item.Match(potential_iter)
                    if result is None:
                        success = False
                        break

                    if isinstance(item, IndentToken):
                        observer.OnIndent()
                    elif isinstance(item, DedentToken):
                        observer.OnDedent()

                    if isinstance(result, list):
                        assert not potential_whitespace

                        for res in result:
                            results.append(
                                Statement.TokenParseResultItem(
                                    item,
                                    potential_whitespace,
                                    res,
                                    potential_iter.Clone(),
                                    IsIgnored=False,
                                ),
                            )
                    else:
                        results.append(
                            Statement.TokenParseResultItem(
                                item,
                                potential_whitespace,
                                result,
                                potential_iter.Clone(),
                                IsIgnored=False,
                            ),
                        )

                    normalized_iter = potential_iter

            else:
                if isinstance(item, Statement):
                    iterator = item.ParseCoroutine(normalized_iter, observer)

                elif isinstance(item, DynamicStatements):
                    iterator = self.ParseMultipleCoroutine(
                        observer.GetDynamicStatements(item),
                        normalized_iter,
                        observer,
                    )

                elif isinstance(item, list):
                    iterator = self.ParseMultipleCoroutine(
                        item,
                        normalized_iter,
                        observer,
                    )

                else:
                    assert False, item

                try:
                    while True:
                        next(iterator)

                        # Yield one or more times
                        while True:
                            status = yield

                            if status == Coroutine.Status.Yield:
                                continue

                            if status == Coroutine.Status.Terminate:
                                iterator.send(status)

                            break

                except StopIteration as ex:
                    if ex.value is None:
                        return None

                    result: Statement.ParseResult = ex.value

                results.append(Statement.StatementParseResultItem(item, result.Results))    # <Has no member> pylint: disable=E1101
                normalized_iter = result.Iter.Clone()                                       # <Has no member> pylint: disable=E1101

                if not result.Success:                                                      # <Has no member> pylint: disable=E1101
                    success = False
                    break

            item_index += 1

        return Statement.ParseResult(success, results, normalized_iter)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    _indent_token                           = IndentToken()
    _dedent_token                           = DedentToken()
    _newline_token                          = NewlineToken()

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
    @classmethod
    def _EatWhitespaceToken(
        cls,
        ignore_whitespace_ctr: int,
        normalized_iter: NormalizedIterator,
    ) -> Optional[List[Statement.TokenParseResultItem]]:
        """Eats any whitespace token when requested"""

        if not ignore_whitespace_ctr:
            return None

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
