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
        CoroutineMock,
        CreateIterator,
        parse_mock,
        InternalStatementMethodCallToTuple,
        MethodCallsToString,
    )

    from ..DynamicStatement import *
    from ..TokenStatement import TokenStatement, RegexToken


# ----------------------------------------------------------------------
class TestStandard(object):
    _lower_statement                        = TokenStatement(RegexToken("lower", re.compile(r"(?P<value>[a-z]+)")))
    _number_statement                       = TokenStatement(RegexToken("number", re.compile(r"(?P<value>[0-9]+)")))

    # ----------------------------------------------------------------------
    def test_Single(self, parse_mock):
        statement = DynamicStatement(lambda observer: [self._lower_statement])

        result = statement.Parse(CreateIterator("word"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or [lower]
                    lower
                        lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 9

        assert [t[1] for t in result.Data.Enum()] == [
            result.Data.Data,
        ]

    # ----------------------------------------------------------------------
    def test_SingleNoMatch(self, parse_mock):
        statement = DynamicStatement(lambda observer: [self._lower_statement])

        result = statement.Parse(CreateIterator("1234"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Or [lower]
                    lower
                        None
            """,
        )

        assert len(parse_mock.method_calls) == 6

    # ----------------------------------------------------------------------
    def test_MultipleNumber(self, parse_mock):
        statement = DynamicStatement(lambda observer: [self._lower_statement, self._number_statement])

        result = statement.Parse(CreateIterator("1234"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or [lower, number]
                    number
                        number <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 11

        assert [t[1] for t in result.Data.Enum()] == [
            result.Data.Data,
        ]

    # ----------------------------------------------------------------------
    def test_MultipleLower(self, parse_mock):
        statement = DynamicStatement(lambda observer: [self._lower_statement, self._number_statement])

        result = statement.Parse(CreateIterator("word"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or [lower, number]
                    lower
                        lower <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert len(parse_mock.method_calls) == 11

        assert [t[1] for t in result.Data.Enum()] == [
            result.Data.Data,
        ]

    # ----------------------------------------------------------------------
    def test_MultipleNumberEvents(self, parse_mock):
        statement = DynamicStatement(lambda observer: [self._lower_statement, self._number_statement])

        result = statement.Parse(
            CreateIterator("1234"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or [lower, number]
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
            0, StartStatementCandidate, ['Dynamic Statements']
            1, StartStatementCandidate, ['Dynamic Statements', 'Or [lower, number]']
            2, StartStatementCandidate, ['Dynamic Statements', 'Or [lower, number]', 0, 'lower']
            3, EndStatementCandidate, ['Dynamic Statements', 'Or [lower, number]', 0, 'lower']
            4, StartStatementCandidate, ['Dynamic Statements', 'Or [lower, number]', 1, 'number']
            5, OnInternalStatementAsync, ['Dynamic Statements', 'Or [lower, number]', 1, 'number']
            6, EndStatementCandidate, ['Dynamic Statements', 'Or [lower, number]', 1, 'number']
            7, OnInternalStatementAsync, ['Dynamic Statements', 'Or [lower, number]']
            8, EndStatementCandidate, ['Dynamic Statements', 'Or [lower, number]']
            9, OnInternalStatementAsync, ['Dynamic Statements']
            10, EndStatementCandidate, ['Dynamic Statements']
            """,
        )

        assert InternalStatementMethodCallToTuple(parse_mock, 5) == (self._number_statement, result.Data.Data.Data, 0, 4)

        # Note that the or statement generated is dynamic, so we cannot compare it directly
        assert InternalStatementMethodCallToTuple(
            parse_mock,
            7,
            use_statement_name=True,
        ) == ("Or [lower, number]", result.Data.Data, 0, 4)

        assert InternalStatementMethodCallToTuple(parse_mock, 9) == (statement, result.Data, 0, 4)

    # ----------------------------------------------------------------------
    def test_SingleNoMatchEvents(self, parse_mock):
        statement = DynamicStatement(lambda observer: [self._lower_statement])

        result = statement.Parse(CreateIterator("1234"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Or [lower]
                    lower
                        None
            """,
        )

        assert len(parse_mock.method_calls) == 6

        assert "{}\n".format(
            "\n".join(
                [
                    "{}, {}, {}".format(
                        index,
                        method_call[0],
                        str(method_call[1][0]),
                    )
                    for index, method_call in enumerate(parse_mock.method_calls)
                ],
            ),
        ) == textwrap.dedent(
            """\
            0, StartStatementCandidate, ['Dynamic Statements']
            1, StartStatementCandidate, ['Dynamic Statements', 'Or [lower]']
            2, StartStatementCandidate, ['Dynamic Statements', 'Or [lower]', 0, 'lower']
            3, EndStatementCandidate, ['Dynamic Statements', 'Or [lower]', 0, 'lower']
            4, EndStatementCandidate, ['Dynamic Statements', 'Or [lower]']
            5, EndStatementCandidate, ['Dynamic Statements']
            """,
        )
