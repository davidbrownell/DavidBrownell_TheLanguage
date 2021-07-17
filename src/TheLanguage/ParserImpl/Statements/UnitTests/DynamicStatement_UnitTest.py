# ----------------------------------------------------------------------
# |
# |  DynamicStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-28 14:50:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for DynamicStatement.py"""

import os
import re
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import (
        CreateIterator,
        MethodCallsToString,
        parse_mock,
    )

    from ..DynamicStatement import *
    from ..TokenStatement import TokenStatement, RegexToken


# ----------------------------------------------------------------------
class TestStandard(object):
    _lower_statement                        = TokenStatement(RegexToken("lower", re.compile(r"(?P<value>[a-z]+)")))
    _number_statement                       = TokenStatement(RegexToken("number", re.compile(r"(?P<value>[0-9]+)")))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Single(self, parse_mock):
        statement = DynamicStatement(lambda unique_id, observer: [self._lower_statement])

        result = await statement.ParseAsync(["root"], CreateIterator("word"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Dynamic Statements
                    Or: {lower}
                        lower
                            lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 9

        assert [t[1] for t in result.Data.Enum()] == [
            result.Data.Data,
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleNoMatch(self, parse_mock):
        statement = DynamicStatement(lambda unique_id, observer: [self._lower_statement])

        result = await statement.ParseAsync(["root"], CreateIterator("1234"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Dynamic Statements
                    Or: {lower}
                        lower
                            <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 6

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleNumber(self, parse_mock):
        statement = DynamicStatement(lambda uniqud_id, observer: [self._lower_statement, self._number_statement])

        result = await statement.ParseAsync(["root"], CreateIterator("1234"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Dynamic Statements
                    Or: {lower, number}
                        number
                            number <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 11

        assert [t[1] for t in result.Data.Enum()] == [
            result.Data.Data,
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleLower(self, parse_mock):
        statement = DynamicStatement(lambda unique_id, observer: [self._lower_statement, self._number_statement])

        result = await statement.ParseAsync(["root"], CreateIterator("word"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Dynamic Statements
                    Or: {lower, number}
                        lower
                            lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 11

        assert [t[1] for t in result.Data.Enum()] == [
            result.Data.Data,
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleNumberEvents(self, parse_mock):
        statement = DynamicStatement(lambda unique_id, observer: [self._lower_statement, self._number_statement])

        result = await statement.ParseAsync(
            ["root"],
            CreateIterator("1234"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Dynamic Statements
                    Or: {lower, number}
                        number
                            number <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 11

        assert [t[1] for t in result.Data.Enum()] == [
            result.Data.Data,
        ]

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Dynamic Statements"
            1) StartStatement, "Or: {lower, number}", "Dynamic Statements"
            2) StartStatement, "lower", "Or: {lower, number}", "Dynamic Statements"
            3) EndStatement, "lower" [False], "Or: {lower, number}" [None], "Dynamic Statements" [None]
            4) StartStatement, "number", "Or: {lower, number}", "Dynamic Statements"
            5) OnInternalStatementAsync, 0, 4
                number
                    number <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
                Or: {lower, number}
                    lower
                        <No Data>
                Dynamic Statements
                    <No Data>
            6) EndStatement, "number" [True], "Or: {lower, number}" [None], "Dynamic Statements" [None]
            7) OnInternalStatementAsync, 0, 4
                Or: {lower, number}
                    number
                        number <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
                Dynamic Statements
                    <No Data>
            8) EndStatement, "Or: {lower, number}" [True], "Dynamic Statements" [None]
            9) OnInternalStatementAsync, 0, 4
                Dynamic Statements
                    Or: {lower, number}
                        number
                            number <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
            10) EndStatement, "Dynamic Statements" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleNoMatchEvents(self, parse_mock):
        statement = DynamicStatement(lambda unique_id, observer: [self._lower_statement])

        result = await statement.ParseAsync(
            ["root"],
            CreateIterator("1234"),
            parse_mock,
            single_threaded=True,
        )
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Dynamic Statements
                    Or: {lower}
                        lower
                            <No Data>
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Dynamic Statements"
            1) StartStatement, "Or: {lower}", "Dynamic Statements"
            2) StartStatement, "lower", "Or: {lower}", "Dynamic Statements"
            3) EndStatement, "lower" [False], "Or: {lower}" [None], "Dynamic Statements" [None]
            4) EndStatement, "Or: {lower}" [False], "Dynamic Statements" [None]
            5) EndStatement, "Dynamic Statements" [False]
            """,
        )
