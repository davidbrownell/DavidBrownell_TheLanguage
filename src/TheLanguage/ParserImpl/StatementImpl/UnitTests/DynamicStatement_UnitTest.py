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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CreateIterator, parse_mock, OnInternalStatementEqual

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

        assert len(parse_mock.method_calls) == 2

        OnInternalStatementEqual(
            parse_mock.method_calls[0],
            self._lower_statement,
            result.Data.Data.Data,
            0,
            result.Iter.Offset,
        )

        OnInternalStatementEqual(
            parse_mock.method_calls[1],
            result.Data.Statement,
            result.Data,
            0,
            result.Iter.Offset,
        )

        tokens = list(result.Data.EnumTokens())

        assert tokens == [result.Data.Data.Data,]

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

        assert len(parse_mock.method_calls) == 0

        tokens = list(result.Data.EnumTokens())

        assert tokens == []

    # ----------------------------------------------------------------------
    def test_Multiple(self, parse_mock):
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

        assert len(parse_mock.method_calls) == 2

        OnInternalStatementEqual(
            parse_mock.method_calls[0],
            self._number_statement,
            result.Data.Data.Data,
            0,
            result.Iter.Offset,
        )

        OnInternalStatementEqual(
            parse_mock.method_calls[1],
            result.Data.Statement,
            result.Data,
            0,
            result.Iter.Offset,
        )

        tokens = list(result.Data.EnumTokens())

        assert tokens == [result.Data.Data.Data,]
