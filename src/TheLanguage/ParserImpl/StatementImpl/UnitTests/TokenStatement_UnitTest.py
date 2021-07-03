# ----------------------------------------------------------------------
# |
# |  TokenStatement_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-27 15:53:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for TokenStatement.py"""

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
    from . import CoroutineMock, CreateIterator, parse_mock

    from ..TokenStatement import *

    from ...Normalize import Normalize
    from ...NormalizedIterator import NormalizedIterator

    from ...Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )


# ----------------------------------------------------------------------
class TestWords(object):
    _word_statement                         = TokenStatement(RegexToken("Word", re.compile(r"(?P<value>[a-zA-Z0-9]+)\b")))
    _newline_statement                      = TokenStatement(NewlineToken())
    _indent_statement                       = TokenStatement(IndentToken())
    _dedent_statement                       = TokenStatement(DedentToken())

    # ----------------------------------------------------------------------
    def test_Match(self, parse_mock):
        iter = CreateIterator("This      is\ta \t\t   test\t  \n")

        # This
        result = self._word_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Word <<Regex: <_sre.SRE_Match object; span=(0, 4), match='This'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 0

        iter = result.Iter

        # is
        result = self._word_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Word <<Regex: <_sre.SRE_Match object; span=(10, 12), match='is'>>> ws:(4, 10) [1, 11 -> 1, 13]
            """,
        )

        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 0

        iter = result.Iter

        # a
        result = self._word_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            14
                Word <<Regex: <_sre.SRE_Match object; span=(13, 14), match='a'>>> ws:(12, 13) [1, 14 -> 1, 15]
            """,
        )

        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 0

        iter = result.Iter

        # test
        result = self._word_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            24
                Word <<Regex: <_sre.SRE_Match object; span=(20, 24), match='test'>>> ws:(14, 20) [1, 21 -> 1, 25]
            """,
        )

        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 0

        iter = result.Iter

        # Newline
        result = self._newline_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            28
                Newline+ <<27, 28>> ws:(24, 27) [1, 28 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()
        assert len(parse_mock.method_calls) == 0

    # ----------------------------------------------------------------------
    def test_NotAMatch(self, parse_mock):
        iter = CreateIterator("te__")

        result = self._word_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                <No Data>
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 0

    # ----------------------------------------------------------------------
    def test_IndentSimple(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock()
        parse_mock.OnDedentAsync = CoroutineMock()

        iter = CreateIterator(
            textwrap.dedent(
                """\
                one
                    two
                """,
            ),
        )

        # One
        result = self._word_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            3
                Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 0

        iter = result.Iter

        # Newline
        result = self._newline_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 0

        iter = result.Iter

        # Indent
        result = self._indent_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            """,
        )

        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 1
        assert parse_mock.method_calls[0] == ("OnIndentAsync", (result.Data,), {})

        iter = result.Iter

        # two
        result = self._word_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            11
                Word <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
            """,
        )

        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 1

        iter = result.Iter

        # Newline
        result = self._newline_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
            """,
        )

        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 1

        iter = result.Iter

        # Dedent
        result = self._dedent_statement.Parse(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Dedent <<>> ws:None [3, 1 -> 3, 1]
            """,
        )

        assert result.Iter.AtEnd()
        assert len(parse_mock.method_calls) == 2
        assert parse_mock.method_calls[1] == ("OnDedentAsync", (result.Data,), {})

    # ----------------------------------------------------------------------
    def test_IndentMoreComplex(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock()
        parse_mock.OnDedentAsync = CoroutineMock()

        iter = CreateIterator(
            textwrap.dedent(
                """\
                one
                    two
                        three
                        four
                    five
                            six
                    seven
                        eight
                """,
            ),
        )

        num_events = 0

        for expected_statement, expected_text in [
            # one
            (self._word_statement, "one"),
            (self._newline_statement, None),

            # two
            (self._indent_statement, None),
            (self._word_statement, "two"),
            (self._newline_statement, None),

            # three
            (self._indent_statement, None),
            (self._word_statement, "three"),
            (self._newline_statement, None),

            # four
            (self._word_statement, "four"),
            (self._newline_statement, None),

            # five
            (self._dedent_statement, None),
            (self._word_statement, "five"),
            (self._newline_statement, None),

            # six
            (self._indent_statement, None),
            (self._word_statement, "six"),
            (self._newline_statement, None),

            # seven
            (self._dedent_statement, None),
            (self._word_statement, "seven"),
            (self._newline_statement, None),

            # eight
            (self._indent_statement, None),
            (self._word_statement, "eight"),
            (self._newline_statement, None),

            # eof
            (self._dedent_statement, None),
            (self._dedent_statement, None),
        ]:
            result = expected_statement.Parse(iter, parse_mock)
            assert result.Success

            if expected_text is not None:
                assert result.Data.Value.Match.group("value") == expected_text

            if expected_statement == self._indent_statement:
                event_name = "OnIndentAsync"
            elif expected_statement == self._dedent_statement:
                event_name = "OnDedentAsync"
            else:
                event_name = None

            if event_name is not None:
                num_events += 1

                assert len(parse_mock.method_calls) == num_events
                assert parse_mock.method_calls[-1] == (event_name, (result.Data,), {})

            iter = result.Iter

        assert iter.AtEnd()
