# ----------------------------------------------------------------------
# |
# |  RepeatStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-28 16:42:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for RepeatStatement.py"""

import os
import re
import textwrap

from unittest.mock import Mock

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
        InternalStatementMethodCallToTuple,
        MethodCallsToString,
        parse_mock,
    )

    from ..OrStatement import OrStatement
    from ..RepeatStatement import *
    from ..TokenStatement import (
        NewlineToken,
        RegexToken,
        TokenStatement,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _word_statement                         = TokenStatement(RegexToken("Word", re.compile(r"(?P<value>[a-zA-Z]+)")))
    _newline_statement                      = TokenStatement(NewlineToken())

    _or_statement                           = OrStatement(_word_statement, _newline_statement)
    _statement                              = RepeatStatement(_or_statement, 2, 4)
    _exact_statement                        = RepeatStatement(_or_statement, 4, 4)

    # ----------------------------------------------------------------------
    def test_MatchSingleLine(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    """,
                ),
            ),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or [Word, Newline+]
                    0) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    1) Newline+
                           Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0, StartStatement, ['Repeat: (Or [Word, Newline+], 2, 4)']
            1, StartStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [0]']
            2, StartStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [0]', 'Or: Word [0]']
            3, OnInternalStatementAsync, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [0]', 'Or: Word [0]']
            4, EndStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [0]', 'Or: Word [0]']
            5, StartStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [0]', 'Or: Newline+ [1]']
            6, EndStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [0]', 'Or: Newline+ [1]']
            7, OnInternalStatementAsync, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [0]']
            8, EndStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [0]']
            9, StartStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [1]']
            10, StartStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [1]', 'Or: Word [0]']
            11, EndStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [1]', 'Or: Word [0]']
            12, StartStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [1]', 'Or: Newline+ [1]']
            13, OnInternalStatementAsync, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [1]', 'Or: Newline+ [1]']
            14, EndStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [1]', 'Or: Newline+ [1]']
            15, OnInternalStatementAsync, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [1]']
            16, EndStatement, ['Repeat: (Or [Word, Newline+], 2, 4)', 'Rpt: Or [Word, Newline+] [1]']
            17, OnInternalStatementAsync, ['Repeat: (Or [Word, Newline+], 2, 4)']
            18, EndStatement, ['Repeat: (Or [Word, Newline+], 2, 4)']
            """,
        )

        assert InternalStatementMethodCallToTuple(parse_mock, 3) == (self._word_statement, result.Data.DataItems[0].Data, 0, 3)
        assert InternalStatementMethodCallToTuple(parse_mock, 7) == (self._or_statement, result.Data.DataItems[0], 0, 3)
        assert InternalStatementMethodCallToTuple(parse_mock, 13) == (self._newline_statement, result.Data.DataItems[1].Data, 3, 4)
        assert InternalStatementMethodCallToTuple(parse_mock, 15) == (self._or_statement, result.Data.DataItems[1], 3, 4)
        assert InternalStatementMethodCallToTuple(parse_mock, 17) == (self._statement, result.Data, 0, 4)

        assert list(result.Data.Enum()) == [
            (self._statement.Statement, result.Data.DataItems[0]),
            (self._statement.Statement, result.Data.DataItems[1]),
        ]

    # ----------------------------------------------------------------------
    def test_MatchTwoLines(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    two
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Or [Word, Newline+]
                    0) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    1) Newline+
                           Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    2) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    3) Newline+
                           Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 35

        assert list(result.Data.Enum()) == [
            (self._statement.Statement, result.Data.DataItems[0]),
            (self._statement.Statement, result.Data.DataItems[1]),
            (self._statement.Statement, result.Data.DataItems[2]),
            (self._statement.Statement, result.Data.DataItems[3]),
        ]

    # ----------------------------------------------------------------------
    def test_MatchThreeLines(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    two
                    three
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Or [Word, Newline+]
                    0) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    1) Newline+
                           Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    2) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    3) Newline+
                           Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 35

        assert list(result.Data.Enum()) == [
            (self._statement.Statement, result.Data.DataItems[0]),
            (self._statement.Statement, result.Data.DataItems[1]),
            (self._statement.Statement, result.Data.DataItems[2]),
            (self._statement.Statement, result.Data.DataItems[3]),
        ]

    # ----------------------------------------------------------------------
    def test_NoMatch(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    123
                    456
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            0
                Or [Word, Newline+]
                    0) Word
                           None
                       Newline+
                           None
            """,
        )

        assert len(parse_mock.method_calls) == 8

        assert list(result.Data.Enum()) == [
            (self._statement.Statement, result.Data.DataItems[0]),
        ]

    # ----------------------------------------------------------------------
    def test_PartialMatch(self, parse_mock):
        result = self._statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    abc123
                    def456
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            3
                Or [Word, Newline+]
                    0) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='abc'>>> ws:None [1, 1 -> 1, 4]
                    1) Word
                           None
                       Newline+
                           None
            """,
        )

        assert len(parse_mock.method_calls) == 16

        assert list(result.Data.Enum()) == [
            (self._statement.Statement, result.Data.DataItems[0]),
            (self._statement.Statement, result.Data.DataItems[1]),
        ]

    # ----------------------------------------------------------------------
    def test_ExactMatch(self, parse_mock):
        result = self._exact_statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    two
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Or [Word, Newline+]
                    0) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    1) Newline+
                           Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    2) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    3) Newline+
                           Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_ExactLimitedMatch(self, parse_mock):
        result = self._exact_statement.Parse(
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    two
                    three
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Or [Word, Newline+]
                    0) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    1) Newline+
                           Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    2) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    3) Newline+
                           Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            """,
        )

    # ----------------------------------------------------------------------
    def test_ExactNoMatch(self, parse_mock):
        result = self._exact_statement.Parse(CreateIterator("one"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            4
                Or [Word, Newline+]
                    0) Word
                           Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    1) Newline+
                           Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            """,
        )

# ----------------------------------------------------------------------
def test_CreationErrors():
    with pytest.raises(AssertionError):
        RepeatStatement(TokenStatement(NewlineToken()), -1, 10)

    with pytest.raises(AssertionError):
        RepeatStatement(TokenStatement(NewlineToken()), 10, 5)

# ----------------------------------------------------------------------
def test_RepeatParseResultDataNoItems():
    statement = TokenStatement(NewlineToken())

    data = RepeatStatement.RepeatParseResultData(statement, [])

    assert str(data) == textwrap.dedent(
        """\
        Newline+
            <No Results>
        """,
    )

    assert list(data.Enum()) == []

# ----------------------------------------------------------------------
def test_RepeatParseResultDataNoneItems():
    statement = TokenStatement(NewlineToken())

    data = RepeatStatement.RepeatParseResultData(statement, [None])

    assert str(data) == textwrap.dedent(
        """\
        Newline+
            0) None
        """,
    )

    assert list(data.Enum()) == [
        (statement, None),
    ]

# ----------------------------------------------------------------------
def test_ParseReturnsNone(parse_mock):
    # ----------------------------------------------------------------------
    class NoneStatement(StatementType):
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

    statement = RepeatStatement(NoneStatement("None Statement"), 1, None)

    result = statement.Parse(CreateIterator("test"), parse_mock)
    assert result is None

# ----------------------------------------------------------------------
def test_OnInternalStatementFalse(parse_mock):
    parse_mock.OnInternalStatementAsync = CoroutineMock(return_value=False)

    statement = RepeatStatement(TokenStatement(NewlineToken()), 1, None)

    result = statement.Parse(
        CreateIterator(
            textwrap.dedent(
                """\




                """,
            ),
        ),
        parse_mock,
    )

    assert result is None
