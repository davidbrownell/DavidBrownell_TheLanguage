# ----------------------------------------------------------------------
# |
# |  OrStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-28 07:05:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for OrStatement.h"""

import os
import re
import textwrap

from typing import Callable, List

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import (
        CoroutineMock,
        CreateIterator,
        parse_mock,
        MethodCallsToString,
    )

    from ..OrStatement import *
    from ..TokenStatement import (
        NewlineToken,
        RegexToken,
        TokenStatement,
    )

    from ...Token import (
        NewlineToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _lower_statement                        = TokenStatement(RegexToken("lower", re.compile(r"(?P<value>[a-z]+[0-9]*)")))
    _upper_statement                        = TokenStatement(RegexToken("upper", re.compile(r"(?P<value>[A-Z]+[0-9]*)")))
    _number_statement                       = TokenStatement(RegexToken("number", re.compile(r"(?P<value>[0-9]+)")))
    _newline_statement                      = TokenStatement(NewlineToken())

    _statement                              = OrStatement(
        _lower_statement,
        _upper_statement,
        _number_statement,
        _newline_statement,
        name="My Or Statement",
    )

    _inner_nested_statement                 = OrStatement(
        _lower_statement,
        _number_statement,
    )

    _outer_nested_statement                 = OrStatement(
        _upper_statement,
        _inner_nested_statement,
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchLower(self, parse_mock):
        iter = CreateIterator("lowercase")

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            9
                My Or Statement
                    lower
                        lower <<Regex: <_sre.SRE_Match object; span=(0, 9), match='lowercase'>>> ws:None [1, 1 -> 1, 10]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchUpper(self, parse_mock):
        iter = CreateIterator("UPPERCASE")

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            9
                My Or Statement
                    upper
                        upper <<Regex: <_sre.SRE_Match object; span=(0, 9), match='UPPERCASE'>>> ws:None [1, 1 -> 1, 10]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNumber(self, parse_mock):
        iter = CreateIterator("12345678")

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            8
                My Or Statement
                    number
                        number <<Regex: <_sre.SRE_Match object; span=(0, 8), match='12345678'>>> ws:None [1, 1 -> 1, 9]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNumberSingleThreaded(self, parse_mock):
        iter = CreateIterator("12345678")

        result = await self._statement.ParseAsync(
            ["root"],
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                My Or Statement
                    number
                        number <<Regex: <_sre.SRE_Match object; span=(0, 8), match='12345678'>>> ws:None [1, 1 -> 1, 9]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_OnInternalStatementReturnsNone(self, parse_mock):
        parse_mock.OnInternalStatementAsync = CoroutineMock(return_value=None)

        iter = CreateIterator("12345678")

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert result is None

        assert len(parse_mock.method_calls) == 11

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                My Or Statement
                    lower
                        <No Data>
                    upper
                        <No Data>
                    number
                        <No Data>
                    Newline+
                        <No Data>
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchSingleThreaded(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = await self._statement.ParseAsync(
            ["root"],
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            0
                My Or Statement
                    lower
                        <No Data>
                    upper
                        <No Data>
                    number
                        <No Data>
                    Newline+
                        <No Data>
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedLower(self, parse_mock):
        result = await self._outer_nested_statement.ParseAsync(
            ["root"],
            CreateIterator("word"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or: {upper, Or: {lower, number}}
                    Or: {lower, number}
                        lower
                            lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 13

        assert list(result.Data.Enum()) == [
            (self._outer_nested_statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedLowerEvents(self, parse_mock):
        result = await self._outer_nested_statement.ParseAsync(
            ["root"],
            CreateIterator("word"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or: {upper, Or: {lower, number}}
                    Or: {lower, number}
                        lower
                            lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Or: {upper, Or: {lower, number}}"
            1) StartStatement, "upper", "Or: {upper, Or: {lower, number}}"
            2) EndStatement, "upper" [False], "Or: {upper, Or: {lower, number}}" [None]
            3) StartStatement, "Or: {lower, number}", "Or: {upper, Or: {lower, number}}"
            4) StartStatement, "lower", "Or: {lower, number}", "Or: {upper, Or: {lower, number}}"
            5) OnInternalStatementAsync, 0, 4
                lower
                    lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
                Or: {lower, number}
                    <No Items>
                Or: {upper, Or: {lower, number}}
                    upper
                        <No Data>
            6) EndStatement, "lower" [True], "Or: {lower, number}" [None], "Or: {upper, Or: {lower, number}}" [None]
            7) StartStatement, "number", "Or: {lower, number}", "Or: {upper, Or: {lower, number}}"
            8) EndStatement, "number" [False], "Or: {lower, number}" [None], "Or: {upper, Or: {lower, number}}" [None]
            9) OnInternalStatementAsync, 0, 4
                Or: {lower, number}
                    lower
                        lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
                Or: {upper, Or: {lower, number}}
                    upper
                        <No Data>
            10) EndStatement, "Or: {lower, number}" [True], "Or: {upper, Or: {lower, number}}" [None]
            11) OnInternalStatementAsync, 0, 4
                Or: {upper, Or: {lower, number}}
                    Or: {lower, number}
                        lower
                            lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            12) EndStatement, "Or: {upper, Or: {lower, number}}" [True]
            """,
        )

        assert list(result.Data.Enum()) == [
            (self._outer_nested_statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedUpper(self, parse_mock):
        result = await self._outer_nested_statement.ParseAsync(
            ["root"],
            CreateIterator("WORD"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or: {upper, Or: {lower, number}}
                    upper
                        upper <<Regex: <_sre.SRE_Match object; span=(0, 4), match='WORD'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._outer_nested_statement, result.Data.Data),
        ]

# ----------------------------------------------------------------------
class TestSort(object):
    _short_statement                        = TokenStatement(RegexToken("Short", re.compile(r"(?P<value>\d\d)")))
    _long_statement                         = TokenStatement(RegexToken("Long", re.compile(r"(?P<value>\d\d\d\d)")))

    _sort_statement                         = OrStatement(
        _short_statement,
        _long_statement,
        name="Sort",
        sort_results=True,
    )

    _no_sort_statement                      = OrStatement(
        _short_statement,
        _long_statement,
        name="No Sort",
        sort_results=False,
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Sort(self, parse_mock):
        iter = CreateIterator("1234")

        result = await self._sort_statement.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Sort
                    Long
                        Long <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 9


    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoSort(self, parse_mock):
        iter = CreateIterator("1234")

        result = await self._no_sort_statement.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            2
                No Sort
                    Short
                        Short <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
            """,
        )

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchNoSort(self, parse_mock):
        result = await self._no_sort_statement.ParseAsync(["root"], CreateIterator("!1122"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                No Sort
                    Short
                        <No Data>
                    Long
                        <No Data>
            """,
        )

        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 6

        assert list(result.Data.Enum()) == [
            (self._no_sort_statement, result.Data.Data),
        ]

# ----------------------------------------------------------------------
class TestParseReturnsNone(object):
    # ----------------------------------------------------------------------
    class EmptyStatement(Statement):
        # ----------------------------------------------------------------------
        @Interface.override
        async def ParseAsync(self, *args, **kwargs):
            return None

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        @Interface.override
        def _PopulateRecursiveImpl(
            self,
            new_statement: Statement,
        ) -> bool:
            # Nothing to do here
            return False

    # ----------------------------------------------------------------------

    _statement                              = OrStatement(
        # Note that we need 2 statements so that the implementation doesn't default to a single thread
        EmptyStatement("1"),
        EmptyStatement("2"),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Standard(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("test"), parse_mock)
        assert result is None

        assert len(parse_mock.method_calls) == 2

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_StandardSingleThreaded(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator("test"),
            parse_mock,
            single_threaded=True,
        )
        assert result is None

        assert len(parse_mock.method_calls) == 2
