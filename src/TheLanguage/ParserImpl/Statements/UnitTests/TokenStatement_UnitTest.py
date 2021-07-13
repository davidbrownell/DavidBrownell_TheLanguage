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
    from . import CoroutineMock, CreateIterator, parse_mock, MethodCallsToString

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
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        iter = CreateIterator("This      is\ta \t\t   test\t  \n")

        # This
        result = await self._word_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(0, 4), match='This'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Word"
            1) OnInternalStatementAsync, 0, 4
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(0, 4), match='This'>>> ws:None [1, 1 -> 1, 5]
            2) EndStatement, "Word" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # is
        result = await self._word_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(10, 12), match='is'>>> ws:(4, 10) [1, 11 -> 1, 13]
            """,
        )

        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Word"
            1) OnInternalStatementAsync, 10, 12
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(10, 12), match='is'>>> ws:(4, 10) [1, 11 -> 1, 13]
            2) EndStatement, "Word" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # a
        result = await self._word_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            14
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(13, 14), match='a'>>> ws:(12, 13) [1, 14 -> 1, 15]
            """,
        )

        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Word"
            1) OnInternalStatementAsync, 13, 14
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(13, 14), match='a'>>> ws:(12, 13) [1, 14 -> 1, 15]
            2) EndStatement, "Word" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # test
        result = await self._word_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            24
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(20, 24), match='test'>>> ws:(14, 20) [1, 21 -> 1, 25]
            """,
        )

        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Word"
            1) OnInternalStatementAsync, 20, 24
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(20, 24), match='test'>>> ws:(14, 20) [1, 21 -> 1, 25]
            2) EndStatement, "Word" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # Newline
        result = await self._newline_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            28
                Newline+
                    Newline+ <<27, 28>> ws:(24, 27) [1, 28 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Newline+"
            1) OnInternalStatementAsync, 27, 28
                Newline+
                    Newline+ <<27, 28>> ws:(24, 27) [1, 28 -> 2, 1]
            2) EndStatement, "Newline+" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NotAMatch(self, parse_mock):
        iter = CreateIterator("te__")

        result = await self._word_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            False
            0
                <No Data>
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Word"
            1) EndStatement, "Word" [False]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_IndentSimple(self, parse_mock):
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
        result = await self._word_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            3
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Word"
            1) OnInternalStatementAsync, 0, 3
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
            2) EndStatement, "Word" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # Newline
        result = await self._newline_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Newline+"
            1) OnInternalStatementAsync, 3, 4
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            2) EndStatement, "Newline+" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # Indent
        result = await self._indent_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Indent
                    Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            """,
        )

        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Indent"
            1) OnIndentAsync, 4, 8
                Indent
                    Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            2) EndStatement, "Indent" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # two
        result = await self._word_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            11
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
            """,
        )

        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Word"
            1) OnInternalStatementAsync, 8, 11
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
            2) EndStatement, "Word" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # Newline
        result = await self._newline_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Newline+
                    Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
            """,
        )

        assert result.Iter.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Newline+"
            1) OnInternalStatementAsync, 11, 12
                Newline+
                    Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
            2) EndStatement, "Newline+" [True]
            """,
        )

        iter = result.Iter
        parse_mock.reset_mock()

        # Dedent
        result = await self._dedent_statement.ParseAsync(iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Dedent
                    Dedent <<>> ws:None [3, 1 -> 3, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Dedent"
            1) OnDedentAsync, 12, 12
                Dedent
                    Dedent <<>> ws:None [3, 1 -> 3, 1]
            2) EndStatement, "Dedent" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_IndentMoreComplex(self, parse_mock):
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

        results = []

        for expected_statement in [
            # one
            self._word_statement,
            self._newline_statement,

            # two
            self._indent_statement,
            self._word_statement,
            self._newline_statement,

            # three
            self._indent_statement,
            self._word_statement,
            self._newline_statement,

            # four
            self._word_statement,
            self._newline_statement,

            # five
            self._dedent_statement,
            self._word_statement,
            self._newline_statement,

            # six
            self._indent_statement,
            self._word_statement,
            self._newline_statement,

            # seven
            self._dedent_statement,
            self._word_statement,
            self._newline_statement,

            # eight
            self._indent_statement,
            self._word_statement,
            self._newline_statement,

            # eof
            self._dedent_statement,
            self._dedent_statement,
        ]:
            results.append(await expected_statement.ParseAsync(iter, parse_mock))
            iter = results[-1].Iter.Clone()

        assert iter.AtEnd()

        assert "\n".join([str(result) for result in results]) == textwrap.dedent(
            """\
            True
            3
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]

            True
            4
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]

            True
            8
                Indent
                    Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]

            True
            11
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]

            True
            12
                Newline+
                    Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]

            True
            20
                Indent
                    Indent <<12, 20, (8)>> ws:None [3, 1 -> 3, 9]

            True
            25
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(20, 25), match='three'>>> ws:None [3, 9 -> 3, 14]

            True
            26
                Newline+
                    Newline+ <<25, 26>> ws:None [3, 14 -> 4, 1]

            True
            38
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(34, 38), match='four'>>> ws:None [4, 9 -> 4, 13]

            True
            39
                Newline+
                    Newline+ <<38, 39>> ws:None [4, 13 -> 5, 1]

            True
            43
                Dedent
                    Dedent <<>> ws:None [5, 1 -> 5, 5]

            True
            47
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(43, 47), match='five'>>> ws:None [5, 5 -> 5, 9]

            True
            48
                Newline+
                    Newline+ <<47, 48>> ws:None [5, 9 -> 6, 1]

            True
            60
                Indent
                    Indent <<48, 60, (12)>> ws:None [6, 1 -> 6, 13]

            True
            63
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(60, 63), match='six'>>> ws:None [6, 13 -> 6, 16]

            True
            64
                Newline+
                    Newline+ <<63, 64>> ws:None [6, 16 -> 7, 1]

            True
            68
                Dedent
                    Dedent <<>> ws:None [7, 1 -> 7, 5]

            True
            73
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(68, 73), match='seven'>>> ws:None [7, 5 -> 7, 10]

            True
            74
                Newline+
                    Newline+ <<73, 74>> ws:None [7, 10 -> 8, 1]

            True
            82
                Indent
                    Indent <<74, 82, (8)>> ws:None [8, 1 -> 8, 9]

            True
            87
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(82, 87), match='eight'>>> ws:None [8, 9 -> 8, 14]

            True
            88
                Newline+
                    Newline+ <<87, 88>> ws:None [8, 14 -> 9, 1]

            True
            88
                Dedent
                    Dedent <<>> ws:None [9, 1 -> 9, 1]

            True
            88
                Dedent
                    Dedent <<>> ws:None [9, 1 -> 9, 1]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Word"
            1) OnInternalStatementAsync, 0, 3
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
            2) EndStatement, "Word" [True]
            3) StartStatement, "Newline+"
            4) OnInternalStatementAsync, 3, 4
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            5) EndStatement, "Newline+" [True]
            6) StartStatement, "Indent"
            7) OnIndentAsync, 4, 8
                Indent
                    Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            8) EndStatement, "Indent" [True]
            9) StartStatement, "Word"
            10) OnInternalStatementAsync, 8, 11
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
            11) EndStatement, "Word" [True]
            12) StartStatement, "Newline+"
            13) OnInternalStatementAsync, 11, 12
                Newline+
                    Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
            14) EndStatement, "Newline+" [True]
            15) StartStatement, "Indent"
            16) OnIndentAsync, 12, 20
                Indent
                    Indent <<12, 20, (8)>> ws:None [3, 1 -> 3, 9]
            17) EndStatement, "Indent" [True]
            18) StartStatement, "Word"
            19) OnInternalStatementAsync, 20, 25
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(20, 25), match='three'>>> ws:None [3, 9 -> 3, 14]
            20) EndStatement, "Word" [True]
            21) StartStatement, "Newline+"
            22) OnInternalStatementAsync, 25, 26
                Newline+
                    Newline+ <<25, 26>> ws:None [3, 14 -> 4, 1]
            23) EndStatement, "Newline+" [True]
            24) StartStatement, "Word"
            25) OnInternalStatementAsync, 34, 38
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(34, 38), match='four'>>> ws:None [4, 9 -> 4, 13]
            26) EndStatement, "Word" [True]
            27) StartStatement, "Newline+"
            28) OnInternalStatementAsync, 38, 39
                Newline+
                    Newline+ <<38, 39>> ws:None [4, 13 -> 5, 1]
            29) EndStatement, "Newline+" [True]
            30) StartStatement, "Dedent"
            31) OnDedentAsync, 39, 43
                Dedent
                    Dedent <<>> ws:None [5, 1 -> 5, 5]
            32) EndStatement, "Dedent" [True]
            33) StartStatement, "Word"
            34) OnInternalStatementAsync, 43, 47
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(43, 47), match='five'>>> ws:None [5, 5 -> 5, 9]
            35) EndStatement, "Word" [True]
            36) StartStatement, "Newline+"
            37) OnInternalStatementAsync, 47, 48
                Newline+
                    Newline+ <<47, 48>> ws:None [5, 9 -> 6, 1]
            38) EndStatement, "Newline+" [True]
            39) StartStatement, "Indent"
            40) OnIndentAsync, 48, 60
                Indent
                    Indent <<48, 60, (12)>> ws:None [6, 1 -> 6, 13]
            41) EndStatement, "Indent" [True]
            42) StartStatement, "Word"
            43) OnInternalStatementAsync, 60, 63
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(60, 63), match='six'>>> ws:None [6, 13 -> 6, 16]
            44) EndStatement, "Word" [True]
            45) StartStatement, "Newline+"
            46) OnInternalStatementAsync, 63, 64
                Newline+
                    Newline+ <<63, 64>> ws:None [6, 16 -> 7, 1]
            47) EndStatement, "Newline+" [True]
            48) StartStatement, "Dedent"
            49) OnDedentAsync, 64, 68
                Dedent
                    Dedent <<>> ws:None [7, 1 -> 7, 5]
            50) EndStatement, "Dedent" [True]
            51) StartStatement, "Word"
            52) OnInternalStatementAsync, 68, 73
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(68, 73), match='seven'>>> ws:None [7, 5 -> 7, 10]
            53) EndStatement, "Word" [True]
            54) StartStatement, "Newline+"
            55) OnInternalStatementAsync, 73, 74
                Newline+
                    Newline+ <<73, 74>> ws:None [7, 10 -> 8, 1]
            56) EndStatement, "Newline+" [True]
            57) StartStatement, "Indent"
            58) OnIndentAsync, 74, 82
                Indent
                    Indent <<74, 82, (8)>> ws:None [8, 1 -> 8, 9]
            59) EndStatement, "Indent" [True]
            60) StartStatement, "Word"
            61) OnInternalStatementAsync, 82, 87
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(82, 87), match='eight'>>> ws:None [8, 9 -> 8, 14]
            62) EndStatement, "Word" [True]
            63) StartStatement, "Newline+"
            64) OnInternalStatementAsync, 87, 88
                Newline+
                    Newline+ <<87, 88>> ws:None [8, 14 -> 9, 1]
            65) EndStatement, "Newline+" [True]
            66) StartStatement, "Dedent"
            67) OnDedentAsync, 88, 88
                Dedent
                    Dedent <<>> ws:None [9, 1 -> 9, 1]
            68) EndStatement, "Dedent" [True]
            69) StartStatement, "Dedent"
            70) OnDedentAsync, 88, 88
                Dedent
                    Dedent <<>> ws:None [9, 1 -> 9, 1]
            71) EndStatement, "Dedent" [True]
            """,
        )
