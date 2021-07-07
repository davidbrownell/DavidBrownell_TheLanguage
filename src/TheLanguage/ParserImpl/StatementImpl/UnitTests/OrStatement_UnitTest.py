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

from unittest.mock import Mock

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
        InternalStatementMethodCallToTuple,
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
    def test_MatchLower(self, parse_mock):
        iter = CreateIterator("lowercase")

        result = self._statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            9
                lower
                    lower <<Regex: <_sre.SRE_Match object; span=(0, 9), match='lowercase'>>> ws:None [1, 1 -> 1, 10]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._lower_statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    def test_MatchUpper(self, parse_mock):
        iter = CreateIterator("UPPERCASE")

        result = self._statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            9
                upper
                    upper <<Regex: <_sre.SRE_Match object; span=(0, 9), match='UPPERCASE'>>> ws:None [1, 1 -> 1, 10]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._upper_statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    def test_MatchNumber(self, parse_mock):
        iter = CreateIterator("12345678")

        result = self._statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            8
                number
                    number <<Regex: <_sre.SRE_Match object; span=(0, 8), match='12345678'>>> ws:None [1, 1 -> 1, 9]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._number_statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    def test_MatchNumberSingleThreaded(self, parse_mock):
        iter = CreateIterator("12345678")

        result = self._statement.Parse(
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                number
                    number <<Regex: <_sre.SRE_Match object; span=(0, 8), match='12345678'>>> ws:None [1, 1 -> 1, 9]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._number_statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    def test_OnInternalStatementReturnsNone(self, parse_mock):
        parse_mock.OnInternalStatementAsync = CoroutineMock(return_value=None)

        iter = CreateIterator("12345678")

        result = self._statement.Parse(iter, parse_mock)
        assert result is None

        assert len(parse_mock.method_calls) == 11

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = self._statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                lower
                    None
                upper
                    None
                number
                    None
                Newline+
                    None
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

        assert list(result.Data.Enum()) == [
            (self._lower_statement, None),
            (self._upper_statement, None),
            (self._number_statement, None),
            (self._newline_statement, None),
        ]

    # ----------------------------------------------------------------------
    def test_NoMatchSingleThreaded(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = self._statement.Parse(
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            0
                lower
                    None
                upper
                    None
                number
                    None
                Newline+
                    None
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

        assert list(result.Data.Enum()) == [
            (self._lower_statement, None),
            (self._upper_statement, None),
            (self._number_statement, None),
            (self._newline_statement, None),
        ]

    # ----------------------------------------------------------------------
    def test_NestedLower(self, parse_mock):
        result = self._outer_nested_statement.Parse(
            CreateIterator("word"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or [lower, number]
                    lower
                        lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 13

        assert list(result.Data.Enum()) == [
            (self._inner_nested_statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    def test_NestedLowerEvents(self, parse_mock):
        result = self._outer_nested_statement.Parse(
            CreateIterator("word"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or [lower, number]
                    lower
                        lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0, StartStatement, ['Or [upper, Or [lower, number]]']
            1, StartStatement, ['Or [upper, Or [lower, number]]', 'Or: upper [0]']
            2, EndStatement, ['Or [upper, Or [lower, number]]', 'Or: upper [0]']
            3, StartStatement, ['Or [upper, Or [lower, number]]', 'Or: Or [lower, number] [1]']
            4, StartStatement, ['Or [upper, Or [lower, number]]', 'Or: Or [lower, number] [1]', 'Or: lower [0]']
            5, OnInternalStatementAsync, ['Or [upper, Or [lower, number]]', 'Or: Or [lower, number] [1]', 'Or: lower [0]']
            6, EndStatement, ['Or [upper, Or [lower, number]]', 'Or: Or [lower, number] [1]', 'Or: lower [0]']
            7, StartStatement, ['Or [upper, Or [lower, number]]', 'Or: Or [lower, number] [1]', 'Or: number [1]']
            8, EndStatement, ['Or [upper, Or [lower, number]]', 'Or: Or [lower, number] [1]', 'Or: number [1]']
            9, OnInternalStatementAsync, ['Or [upper, Or [lower, number]]', 'Or: Or [lower, number] [1]']
            10, EndStatement, ['Or [upper, Or [lower, number]]', 'Or: Or [lower, number] [1]']
            11, OnInternalStatementAsync, ['Or [upper, Or [lower, number]]']
            12, EndStatement, ['Or [upper, Or [lower, number]]']
            """,
        )

        assert InternalStatementMethodCallToTuple(parse_mock, 5) == (self._lower_statement, result.Data.Data.Data, 0, 4)
        assert InternalStatementMethodCallToTuple(parse_mock, 9) == (self._inner_nested_statement, result.Data.Data, 0, 4)
        assert InternalStatementMethodCallToTuple(parse_mock, 11) == (self._outer_nested_statement, result.Data, 0, 4)

        assert list(result.Data.Enum()) == [
            (self._inner_nested_statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    def test_NestedUpper(self, parse_mock):
        result = self._outer_nested_statement.Parse(
            CreateIterator("WORD"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                upper
                    upper <<Regex: <_sre.SRE_Match object; span=(0, 4), match='WORD'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 12

        assert list(result.Data.Enum()) == [
            (self._upper_statement, result.Data.Data),
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
    def test_Sort(self, parse_mock):
        iter = CreateIterator("1234")

        result = self._sort_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Long
                    Long <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 9


    # ----------------------------------------------------------------------
    def test_NoSort(self, parse_mock):
        iter = CreateIterator("1234")

        result = self._no_sort_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            2
                Short
                    Short <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
            """,
        )

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    def test_NoMatchNoSort(self, parse_mock):
        result = self._no_sort_statement.Parse(CreateIterator("!1122"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Short
                    None
                Long
                    None
            """,
        )

        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 6

        assert list(result.Data.Enum()) == [
            (self._short_statement, None),
            (self._long_statement, None),
        ]

# ----------------------------------------------------------------------
class TestParseReturnsNone(object):
    # ----------------------------------------------------------------------
    class EmptyStatement(Statement):
        # ----------------------------------------------------------------------
        @Interface.override
        def Clone(
            self,
            unique_id: List[Any],
        ):
            return self.__class__(
                self.Name,
                unique_id=unique_id,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def ParseAsync(self, *args, **kwargs):
            return None

    # ----------------------------------------------------------------------

    _statement                              = OrStatement(
        # Note that we need 2 statements so that the implementation doesn't default to a single thread
        EmptyStatement("1"),
        EmptyStatement("2"),
    )

    # ----------------------------------------------------------------------
    def test_Standard(self, parse_mock):
        result = self._statement.Parse(CreateIterator("test"), parse_mock)
        assert result is None

        assert len(parse_mock.method_calls) == 2

    # ----------------------------------------------------------------------
    def test_StandardSingleThreaded(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator("test"),
            parse_mock,
            single_threaded=True,
        )
        assert result is None

        assert len(parse_mock.method_calls) == 2
