# ----------------------------------------------------------------------
# |
# |  StatementDSL_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-12 16:26:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tst for StatementDSL.py"""

import os

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..StatementDSL import *

    from ...Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
    )

    from ...Components.UnitTests import (
        CoroutineMock,
        CreateIterator,
        parse_mock,
        MethodCallsToString,
    )


# ----------------------------------------------------------------------
_word_token                                 = RegexToken("Word Token", re.compile(r"(?P<value>[a-z]+)"))
_number_token                               = RegexToken("Number Token", re.compile(r"(?P<value>\d+)"))
_upper_token                                = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
_lpar_token                                 = RegexToken("lpar", re.compile(r"\("))
_rpar_token                                 = RegexToken("rpar", re.compile(r"\)"))

# ----------------------------------------------------------------------
class TestParseSimple(object):
    _statement                              = CreateStatement(
        name="Statement",
        item=[
            _word_token,
            _word_token,
            NewlineToken(),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleSpaceSep(self, parse_mock):
        iter = CreateIterator("one two")

        assert str(iter) == "0 8 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 8 0 None None", "The incoming iterator should not be modified"
        assert str(result.Iter) == "8 8 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleSpaceSep(self, parse_mock):
        iter = CreateIterator("one      two")

        assert str(iter) == "0 13 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 13 0 None None", "The incoming iterator should not be modified"
        assert str(result.Iter) == "13 13 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            13
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(9, 12), match='two'>>> ws:(3, 9) [1, 10 -> 1, 13]
                    Newline+
                        Newline+ <<12, 13>> ws:None [1, 13 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TabSep(self, parse_mock):
        iter = CreateIterator("one\ttwo")

        assert str(iter) == "0 8 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 8 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "8 8 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultiTabSep(self, parse_mock):
        iter = CreateIterator("one\t\ttwo")

        assert str(iter) == "0 9 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 9 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "9 9 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(5, 8), match='two'>>> ws:(3, 5) [1, 6 -> 1, 9]
                    Newline+
                        Newline+ <<8, 9>> ws:None [1, 9 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TrailingSpace(self, parse_mock):
        iter = CreateIterator("one two ")

        assert str(iter) == "0 9 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 9 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "9 9 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<8, 9>> ws:(7, 8) [1, 9 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleTrailingSpace(self, parse_mock):
        iter = CreateIterator("one two    ")

        assert str(iter) == "0 12 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 12 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "12 12 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:(7, 11) [1, 12 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TrailingTab(self, parse_mock):
        iter = CreateIterator("one two\t")

        assert str(iter) == "0 9 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 9 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "9 9 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<8, 9>> ws:(7, 8) [1, 9 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleTrailingTab(self, parse_mock):
        iter = CreateIterator("one two\t\t\t\t")

        assert str(iter) == "0 12 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 12 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "12 12 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            12
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:(7, 11) [1, 12 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleLines(self, parse_mock):
        iter = CreateIterator(
            textwrap.dedent(
                """\
                one two
                three four
                """,
            ),
        )

        # Line 1
        assert str(iter) == "0 19 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 19 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "8 19 1 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<7, 8>> ws:None [1, 8 -> 2, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 12

        iter = result.Iter

        # Line 2
        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "8 19 1 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "19 19 2 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            19
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='three'>>> ws:None [2, 1 -> 2, 6]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(14, 18), match='four'>>> ws:(13, 14) [2, 7 -> 2, 11]
                    Newline+
                        Newline+ <<18, 19>> ws:None [2, 11 -> 3, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 24

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TrailingWhitespace(self, parse_mock):
        iter = CreateIterator("one two\n\n  \n    \n")

        assert str(iter) == "0 17 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 17 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "17 17 4 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            True
            17
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        Newline+ <<7, 17>> ws:None [1, 8 -> 5, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        iter = CreateIterator("one two three")

        assert str(iter) == "0 14 0 None None"

        result = await self._statement.ParseAsync(["root"], iter, parse_mock)
        assert str(iter) == "0 14 0 None None",  "The incoming iterator should not be modified"
        assert str(result.Iter) == "7 14 0 None None", "The result iterator should be modified"

        assert str(result) == textwrap.dedent(
            """\
            False
            7
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:(3, 4) [1, 5 -> 1, 8]
                    Newline+
                        <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 10

# ----------------------------------------------------------------------
class TestParseIndentAndDedent(object):
    _statement                              = CreateStatement(
        name="Statement",
        item=[
            _word_token,
            NewlineToken(),
            IndentToken(),
            _word_token,
            NewlineToken(),
            _word_token,
            NewlineToken(),
            DedentToken(),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
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
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            22
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                    Newline+
                        Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
                    Dedent
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Statement"
            1) StartStatement, "Word Token", "Statement"
            2) OnInternalStatementAsync, 0, 3
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Statement
                    <No Items>
            3) EndStatement, "Word Token" [True], "Statement" [None]
            4) StartStatement, "Newline+", "Statement"
            5) OnInternalStatementAsync, 3, 4
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
            6) EndStatement, "Newline+" [True], "Statement" [None]
            7) StartStatement, "Indent", "Statement"
            8) OnIndentAsync, 4, 8
                Indent
                    Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            9) EndStatement, "Indent" [True], "Statement" [None]
            10) StartStatement, "Word Token", "Statement"
            11) OnInternalStatementAsync, 8, 11
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
            12) EndStatement, "Word Token" [True], "Statement" [None]
            13) StartStatement, "Newline+", "Statement"
            14) OnInternalStatementAsync, 11, 12
                Newline+
                    Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
            15) EndStatement, "Newline+" [True], "Statement" [None]
            16) StartStatement, "Word Token", "Statement"
            17) OnInternalStatementAsync, 16, 21
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
            18) EndStatement, "Word Token" [True], "Statement" [None]
            19) StartStatement, "Newline+", "Statement"
            20) OnInternalStatementAsync, 21, 22
                Newline+
                    Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
            21) EndStatement, "Newline+" [True], "Statement" [None]
            22) StartStatement, "Dedent", "Statement"
            23) OnDedentAsync, 22, 22
                Dedent
                    Dedent <<>> ws:None [4, 1 -> 4, 1]
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                    Newline+
                        Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
            24) EndStatement, "Dedent" [True], "Statement" [None]
            25) OnInternalStatementAsync, 0, 22
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='three'>>> ws:None [3, 5 -> 3, 10]
                    Newline+
                        Newline+ <<21, 22>> ws:None [3, 10 -> 4, 1]
                    Dedent
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            26) EndStatement, "Statement" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
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
            False
            12
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        Indent <<4, 8, (4)>> ws:None [2, 1 -> 2, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='two'>>> ws:None [2, 5 -> 2, 8]
                    Newline+
                        Newline+ <<11, 12>> ws:None [2, 8 -> 3, 1]
                    Word Token
                        <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 19

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_FinishEarly(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            4
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Indent
                        <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 10

# ----------------------------------------------------------------------
class TestIgnoreWhitespace(object):
    _statement                              = CreateStatement(
        name="Statement",
        item=[
            _word_token,
            _lpar_token,
            PushIgnoreWhitespaceControlToken(),
            _word_token,
            _word_token,
            _word_token,
            _word_token,
            PopIgnoreWhitespaceControlToken(),
            _rpar_token,
            _word_token,
            NewlineToken(),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNoExtra(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    one (


                        two

                            three
                        four
                            five

                    ) six
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            60
                Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(4, 5), match='('>>> ws:(3, 4) [1, 5 -> 1, 6]
                    Newline+ <<5, 8>> ws:None !Ignored! [1, 6 -> 4, 1]
                    Indent <<8, 12, (4)>> ws:None !Ignored! [4, 1 -> 4, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='two'>>> ws:None [4, 5 -> 4, 8]
                    Newline+ <<15, 17>> ws:None !Ignored! [4, 8 -> 6, 1]
                    Indent <<17, 25, (8)>> ws:None !Ignored! [6, 1 -> 6, 9]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(25, 30), match='three'>>> ws:None [6, 9 -> 6, 14]
                    Newline+ <<30, 31>> ws:None !Ignored! [6, 14 -> 7, 1]
                    Dedent <<>> ws:None !Ignored! [7, 1 -> 7, 5]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(35, 39), match='four'>>> ws:None [7, 5 -> 7, 9]
                    Newline+ <<39, 40>> ws:None !Ignored! [7, 9 -> 8, 1]
                    Indent <<40, 48, (8)>> ws:None !Ignored! [8, 1 -> 8, 9]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(48, 52), match='five'>>> ws:None [8, 9 -> 8, 13]
                    Newline+ <<52, 54>> ws:None !Ignored! [8, 13 -> 10, 1]
                    Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                    Dedent <<>> ws:None !Ignored! [10, 1 -> 10, 1]
                    rpar
                        rpar <<Regex: <_sre.SRE_Match object; span=(54, 55), match=')'>>> ws:None [10, 1 -> 10, 2]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(56, 59), match='six'>>> ws:(55, 56) [10, 3 -> 10, 6]
                    Newline+
                        Newline+ <<59, 60>> ws:None [10, 6 -> 11, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 30

# ----------------------------------------------------------------------
class TestEmbeddedStatements(object):
    _inner_statement                        = CreateStatement(
        name="Inner",
        item=[
            _word_token,
            _word_token,
        ],
    )

    _statement                              = CreateStatement(
        name="Statement",
        item=[
            _lpar_token,
            _inner_statement,
            _rpar_token,
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator("( one two )"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            11
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Inner
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
                    rpar
                        rpar <<Regex: <_sre.SRE_Match object; span=(10, 11), match=')'>>> ws:(9, 10) [1, 11 -> 1, 12]
            """,
        )

        # assert result.Iter.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Statement"
            1) StartStatement, "lpar", "Statement"
            2) OnInternalStatementAsync, 0, 1
                lpar
                    lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                Statement
                    <No Items>
            3) EndStatement, "lpar" [True], "Statement" [None]
            4) StartStatement, "Inner", "Statement"
            5) StartStatement, "Word Token", "Inner", "Statement"
            6) OnInternalStatementAsync, 2, 5
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                Inner
                    <No Items>
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
            7) EndStatement, "Word Token" [True], "Inner" [None], "Statement" [None]
            8) StartStatement, "Word Token", "Inner", "Statement"
            9) OnInternalStatementAsync, 6, 9
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
                Inner
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
            10) EndStatement, "Word Token" [True], "Inner" [None], "Statement" [None]
            11) OnInternalStatementAsync, 1, 9
                Inner
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
            12) EndStatement, "Inner" [True], "Statement" [None]
            13) StartStatement, "rpar", "Statement"
            14) OnInternalStatementAsync, 10, 11
                rpar
                    rpar <<Regex: <_sre.SRE_Match object; span=(10, 11), match=')'>>> ws:(9, 10) [1, 11 -> 1, 12]
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Inner
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
            15) EndStatement, "rpar" [True], "Statement" [None]
            16) OnInternalStatementAsync, 0, 11
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Inner
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
                    rpar
                        rpar <<Regex: <_sre.SRE_Match object; span=(10, 11), match=')'>>> ws:(9, 10) [1, 11 -> 1, 12]
            17) EndStatement, "Statement" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchAllInner(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("( one two"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            9
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Inner
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
                    rpar
                        <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 16

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchPartialInner(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("( one"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            5
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Inner
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(2, 5), match='one'>>> ws:(1, 2) [1, 3 -> 1, 6]
                        Word Token
                            <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchFirstOnly(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("( "), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            1
                Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Inner
                        Word Token
                            <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 9

# ----------------------------------------------------------------------
class TestDynamicStatements(object):
    _word_statement                         = CreateStatement(
        name="Word Statement",
        item=[
            _word_token,
            _word_token,
            NewlineToken(),
        ],
    )

    _number_statement                       = CreateStatement(
        name="Number Statement",
        item=[
            _number_token,
            NewlineToken(),
        ],
    )

    _statement                              = CreateStatement(
        name="Statement",
        item=[
            DynamicStatements.Statements,
            DynamicStatements.Statements,
            DynamicStatements.Expressions,
        ],
    )

    # ----------------------------------------------------------------------
    @staticmethod
    @pytest.fixture
    def modified_parse_mock(parse_mock):
        parse_mock.GetDynamicStatements.side_effect = lambda unique_id, value: [TestDynamicStatements._word_statement, TestDynamicStatements._number_statement] if value == DynamicStatements.Statements else [TestDynamicStatements._number_statement]

        return parse_mock

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, modified_parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda wordb
                    123
                    456
                    """,
                ),
            ),
            modified_parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            20
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                    DynamicStatements.Expressions
                        Or: {Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 1 -> 3, 4]
                                Newline+
                                    Newline+ <<19, 20>> ws:None [3, 4 -> 4, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert MethodCallsToString(modified_parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Statement"
            1) StartStatement, "DynamicStatements.Statements", "Statement"
            2) GetDynamicStatements, e
            3) StartStatement, "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            4) StartStatement, "Word Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            5) StartStatement, "Word Token", "Word Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            6) OnInternalStatementAsync, 0, 5
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                Word Statement
                    <No Items>
                Or: {Word Statement, Number Statement}
                    <No Items>
                DynamicStatements.Statements
                    <No Data>
                Statement
                    <No Items>
            7) EndStatement, "Word Token" [True], "Word Statement" [None], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            8) StartStatement, "Word Token", "Word Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            9) OnInternalStatementAsync, 6, 11
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                Word Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                Or: {Word Statement, Number Statement}
                    <No Items>
                DynamicStatements.Statements
                    <No Data>
                Statement
                    <No Items>
            10) EndStatement, "Word Token" [True], "Word Statement" [None], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            11) StartStatement, "Newline+", "Word Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            12) OnInternalStatementAsync, 11, 12
                Newline+
                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                Word Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                Or: {Word Statement, Number Statement}
                    <No Items>
                DynamicStatements.Statements
                    <No Data>
                Statement
                    <No Items>
            13) EndStatement, "Newline+" [True], "Word Statement" [None], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            14) OnInternalStatementAsync, 0, 12
                Word Statement
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                    Newline+
                        Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                Or: {Word Statement, Number Statement}
                    <No Items>
                DynamicStatements.Statements
                    <No Data>
                Statement
                    <No Items>
            15) EndStatement, "Word Statement" [True], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            16) StartStatement, "Number Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            17) StartStatement, "Number Token", "Number Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            18) EndStatement, "Number Token" [False], "Number Statement" [None], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            19) EndStatement, "Number Statement" [False], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            20) OnInternalStatementAsync, 0, 12
                Or: {Word Statement, Number Statement}
                    Word Statement
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                        Newline+
                            Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                DynamicStatements.Statements
                    <No Data>
                Statement
                    <No Items>
            21) EndStatement, "Or: {Word Statement, Number Statement}" [True], "DynamicStatements.Statements" [None], "Statement" [None]
            22) OnInternalStatementAsync, 0, 12
                DynamicStatements.Statements
                    Or: {Word Statement, Number Statement}
                        Word Statement
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                            Newline+
                                Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                Statement
                    <No Items>
            23) EndStatement, "DynamicStatements.Statements" [True], "Statement" [None]
            24) StartStatement, "DynamicStatements.Statements", "Statement"
            25) GetDynamicStatements, e
            26) StartStatement, "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            27) StartStatement, "Word Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            28) StartStatement, "Word Token", "Word Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            29) EndStatement, "Word Token" [False], "Word Statement" [None], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            30) EndStatement, "Word Statement" [False], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            31) StartStatement, "Number Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            32) StartStatement, "Number Token", "Number Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            33) OnInternalStatementAsync, 12, 15
                Number Token
                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                Number Statement
                    <No Items>
                Or: {Word Statement, Number Statement}
                    Word Statement
                        Word Token
                            <No Data>
                DynamicStatements.Statements
                    <No Data>
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
            34) EndStatement, "Number Token" [True], "Number Statement" [None], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            35) StartStatement, "Newline+", "Number Statement", "Or: {Word Statement, Number Statement}", "DynamicStatements.Statements", "Statement"
            36) OnInternalStatementAsync, 15, 16
                Newline+
                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                Number Statement
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                Or: {Word Statement, Number Statement}
                    Word Statement
                        Word Token
                            <No Data>
                DynamicStatements.Statements
                    <No Data>
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
            37) EndStatement, "Newline+" [True], "Number Statement" [None], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            38) OnInternalStatementAsync, 12, 16
                Number Statement
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                    Newline+
                        Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                Or: {Word Statement, Number Statement}
                    Word Statement
                        Word Token
                            <No Data>
                DynamicStatements.Statements
                    <No Data>
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
            39) EndStatement, "Number Statement" [True], "Or: {Word Statement, Number Statement}" [None], "DynamicStatements.Statements" [None], "Statement" [None]
            40) OnInternalStatementAsync, 12, 16
                Or: {Word Statement, Number Statement}
                    Number Statement
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                        Newline+
                            Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                DynamicStatements.Statements
                    <No Data>
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
            41) EndStatement, "Or: {Word Statement, Number Statement}" [True], "DynamicStatements.Statements" [None], "Statement" [None]
            42) OnInternalStatementAsync, 12, 16
                DynamicStatements.Statements
                    Or: {Word Statement, Number Statement}
                        Number Statement
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                            Newline+
                                Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
            43) EndStatement, "DynamicStatements.Statements" [True], "Statement" [None]
            44) StartStatement, "DynamicStatements.Expressions", "Statement"
            45) GetDynamicStatements, e
            46) StartStatement, "Or: {Number Statement}", "DynamicStatements.Expressions", "Statement"
            47) StartStatement, "Number Statement", "Or: {Number Statement}", "DynamicStatements.Expressions", "Statement"
            48) StartStatement, "Number Token", "Number Statement", "Or: {Number Statement}", "DynamicStatements.Expressions", "Statement"
            49) OnInternalStatementAsync, 16, 19
                Number Token
                    Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 1 -> 3, 4]
                Number Statement
                    <No Items>
                Or: {Number Statement}
                    <No Items>
                DynamicStatements.Expressions
                    <No Data>
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
            50) EndStatement, "Number Token" [True], "Number Statement" [None], "Or: {Number Statement}" [None], "DynamicStatements.Expressions" [None], "Statement" [None]
            51) StartStatement, "Newline+", "Number Statement", "Or: {Number Statement}", "DynamicStatements.Expressions", "Statement"
            52) OnInternalStatementAsync, 19, 20
                Newline+
                    Newline+ <<19, 20>> ws:None [3, 4 -> 4, 1]
                Number Statement
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 1 -> 3, 4]
                Or: {Number Statement}
                    <No Items>
                DynamicStatements.Expressions
                    <No Data>
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
            53) EndStatement, "Newline+" [True], "Number Statement" [None], "Or: {Number Statement}" [None], "DynamicStatements.Expressions" [None], "Statement" [None]
            54) OnInternalStatementAsync, 16, 20
                Number Statement
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 1 -> 3, 4]
                    Newline+
                        Newline+ <<19, 20>> ws:None [3, 4 -> 4, 1]
                Or: {Number Statement}
                    <No Items>
                DynamicStatements.Expressions
                    <No Data>
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
            55) EndStatement, "Number Statement" [True], "Or: {Number Statement}" [None], "DynamicStatements.Expressions" [None], "Statement" [None]
            56) OnInternalStatementAsync, 16, 20
                Or: {Number Statement}
                    Number Statement
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 1 -> 3, 4]
                        Newline+
                            Newline+ <<19, 20>> ws:None [3, 4 -> 4, 1]
                DynamicStatements.Expressions
                    <No Data>
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
            57) EndStatement, "Or: {Number Statement}" [True], "DynamicStatements.Expressions" [None], "Statement" [None]
            58) OnInternalStatementAsync, 16, 20
                DynamicStatements.Expressions
                    Or: {Number Statement}
                        Number Statement
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 1 -> 3, 4]
                            Newline+
                                Newline+ <<19, 20>> ws:None [3, 4 -> 4, 1]
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
            59) EndStatement, "DynamicStatements.Expressions" [True], "Statement" [None]
            60) OnInternalStatementAsync, 0, 20
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                    DynamicStatements.Expressions
                        Or: {Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [3, 1 -> 3, 4]
                                Newline+
                                    Newline+ <<19, 20>> ws:None [3, 4 -> 4, 1]
            61) EndStatement, "Statement" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, modified_parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda wordb
                    123
                    wordc wordd
                    """,
                ),
            ),
            modified_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            16
                Statement
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Word Statement
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                Newline+
                                    Newline+ <<11, 12>> ws:None [1, 12 -> 2, 1]
                    DynamicStatements.Statements
                        Or: {Word Statement, Number Statement}
                            Number Statement
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [2, 1 -> 2, 4]
                                Newline+
                                    Newline+ <<15, 16>> ws:None [2, 4 -> 3, 1]
                    DynamicStatements.Expressions
                        Or: {Number Statement}
                            Number Statement
                                Number Token
                                    <No Data>
            """,
        )

        assert len(modified_parse_mock.method_calls) == 54

# ----------------------------------------------------------------------
class TestOrStatements(object):
    _word_statement                         = CreateStatement(
        name="Word Statement",
        item=[
            _word_token,
            NewlineToken(),
        ],
    )

    _number_statement                       = CreateStatement(
        name="Number Statement",
        item=[
            _number_token,
            NewlineToken(),
        ],
    )

    _upper_statement                        = CreateStatement(
        name="Upper Statement",
        item=[
            _upper_token,
            NewlineToken(),
        ],
    )

    _statement                              = CreateStatement(
        item=(
            _word_statement,
            _number_statement,
            _upper_statement,
        ),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_WordMatch(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("word"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            5
                Or: {Word Statement, Number Statement, Upper Statement}
                    Word Statement
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
                        Newline+
                            Newline+ <<4, 5>> ws:None [1, 5 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 20

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NumberMatch(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("1234"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            5
                Or: {Word Statement, Number Statement, Upper Statement}
                    Number Statement
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='1234'>>> ws:None [1, 1 -> 1, 5]
                        Newline+
                            Newline+ <<4, 5>> ws:None [1, 5 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 20

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_UpperMatch(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("WORD"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            5
                Or: {Word Statement, Number Statement, Upper Statement}
                    Upper Statement
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='WORD'>>> ws:None [1, 1 -> 1, 5]
                        Newline+
                            Newline+ <<4, 5>> ws:None [1, 5 -> 2, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 20

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator("this is not a match"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            4
                Or: {Word Statement, Number Statement, Upper Statement}
                    Word Statement
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='this'>>> ws:None [1, 1 -> 1, 5]
                        Newline+
                            <No Data>
                    Number Statement
                        Number Token
                            <No Data>
                    Upper Statement
                        Upper Token
                            <No Data>
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Or: {Word Statement, Number Statement, Upper Statement}"
            1) StartStatement, "Word Statement", "Or: {Word Statement, Number Statement, Upper Statement}"
            2) StartStatement, "Word Token", "Word Statement", "Or: {Word Statement, Number Statement, Upper Statement}"
            3) OnInternalStatementAsync, 0, 4
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='this'>>> ws:None [1, 1 -> 1, 5]
                Word Statement
                    <No Items>
                Or: {Word Statement, Number Statement, Upper Statement}
                    <No Items>
            4) EndStatement, "Word Token" [True], "Word Statement" [None], "Or: {Word Statement, Number Statement, Upper Statement}" [None]
            5) StartStatement, "Newline+", "Word Statement", "Or: {Word Statement, Number Statement, Upper Statement}"
            6) EndStatement, "Newline+" [False], "Word Statement" [None], "Or: {Word Statement, Number Statement, Upper Statement}" [None]
            7) EndStatement, "Word Statement" [False], "Or: {Word Statement, Number Statement, Upper Statement}" [None]
            8) StartStatement, "Number Statement", "Or: {Word Statement, Number Statement, Upper Statement}"
            9) StartStatement, "Number Token", "Number Statement", "Or: {Word Statement, Number Statement, Upper Statement}"
            10) EndStatement, "Number Token" [False], "Number Statement" [None], "Or: {Word Statement, Number Statement, Upper Statement}" [None]
            11) EndStatement, "Number Statement" [False], "Or: {Word Statement, Number Statement, Upper Statement}" [None]
            12) StartStatement, "Upper Statement", "Or: {Word Statement, Number Statement, Upper Statement}"
            13) StartStatement, "Upper Token", "Upper Statement", "Or: {Word Statement, Number Statement, Upper Statement}"
            14) EndStatement, "Upper Token" [False], "Upper Statement" [None], "Or: {Word Statement, Number Statement, Upper Statement}" [None]
            15) EndStatement, "Upper Statement" [False], "Or: {Word Statement, Number Statement, Upper Statement}" [None]
            16) EndStatement, "Or: {Word Statement, Number Statement, Upper Statement}" [False]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EarlyTermination(self, parse_mock):
        parse_mock.OnInternalStatementAsync = CoroutineMock(
            side_effect=[True, False],
        )

        result = await self._statement.ParseAsync(["root"], CreateIterator("word"), parse_mock)

        assert result is None
        assert len(parse_mock.method_calls) == 18

# ----------------------------------------------------------------------
class TestEmbeddedOrStatements(object):
    _statement                              = CreateStatement(
        (
            [_word_token, NewlineToken()],
            [_number_token, NewlineToken()],
            [_upper_token, NewlineToken()],
        ),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Standard(self, parse_mock):
        iter = CreateIterator(
            textwrap.dedent(
                """\
                one
                2222
                THREE
                """,
            ),
        )

        # Line 1
        result = await self._statement.ParseAsync(["root"], iter, parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Or: {Sequence: [Word Token, Newline+], Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+]}
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            """,
        )

        iter = result.Iter

        # Line 2
        result = await self._statement.ParseAsync(["root"], iter, parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Or: {Sequence: [Word Token, Newline+], Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+]}
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(4, 8), match='2222'>>> ws:None [2, 1 -> 2, 5]
                        Newline+
                            Newline+ <<8, 9>> ws:None [2, 5 -> 3, 1]
            """,
        )

        iter = result.Iter

        # Line 3
        result = await self._statement.ParseAsync(["root"], iter, parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            15
                Or: {Sequence: [Word Token, Newline+], Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+]}
                    Sequence: [Upper Token, Newline+]
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(9, 14), match='THREE'>>> ws:None [3, 1 -> 3, 6]
                        Newline+
                            Newline+ <<14, 15>> ws:None [3, 6 -> 4, 1]
            """,
        )

        iter = result.Iter

        # Done
        assert iter.AtEnd()

# ----------------------------------------------------------------------
class TestRepeatStatements(object):
    _statement                              = CreateStatement(
        [
            StatementItem([_word_token, NewlineToken()], arity="*"),
            StatementItem([_number_token, NewlineToken()], arity="+"),
            StatementItem([_upper_token, NewlineToken()], arity="?"),
            StatementItem([_word_token, NewlineToken()], arity="+"),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match1(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    wordb
                    12
                    3456
                    UPPER
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            44
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                            Newline+
                                Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:None [2, 1 -> 2, 6]
                            Newline+
                                Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(12, 14), match='12'>>> ws:None [3, 1 -> 3, 3]
                            Newline+
                                Newline+ <<14, 15>> ws:None [3, 3 -> 4, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(15, 19), match='3456'>>> ws:None [4, 1 -> 4, 5]
                            Newline+
                                Newline+ <<19, 20>> ws:None [4, 5 -> 5, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        Sequence: [Upper Token, Newline+]
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='UPPER'>>> ws:None [5, 1 -> 5, 6]
                            Newline+
                                Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                    Repeat: (Sequence: [Word Token, Newline+], 1, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='wordc'>>> ws:None [6, 1 -> 6, 6]
                            Newline+
                                Newline+ <<31, 32>> ws:None [6, 6 -> 7, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(32, 37), match='wordd'>>> ws:None [7, 1 -> 7, 6]
                            Newline+
                                Newline+ <<37, 38>> ws:None [7, 6 -> 8, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(38, 43), match='worde'>>> ws:None [8, 1 -> 8, 6]
                            Newline+
                                Newline+ <<43, 44>> ws:None [8, 6 -> 9, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 95

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match2(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    12
                    3456
                    UPPER
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            32
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        Sequence: [Upper Token, Newline+]
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='UPPER'>>> ws:None [3, 1 -> 3, 6]
                            Newline+
                                Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                    Repeat: (Sequence: [Word Token, Newline+], 1, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordc'>>> ws:None [4, 1 -> 4, 6]
                            Newline+
                                Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='wordd'>>> ws:None [5, 1 -> 5, 6]
                            Newline+
                                Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='worde'>>> ws:None [6, 1 -> 6, 6]
                            Newline+
                                Newline+ <<31, 32>> ws:None [6, 6 -> 7, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 77

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match3(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    12
                    3456
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            32
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                            Newline+
                                Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(6, 8), match='12'>>> ws:None [2, 1 -> 2, 3]
                            Newline+
                                Newline+ <<8, 9>> ws:None [2, 3 -> 3, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(9, 13), match='3456'>>> ws:None [3, 1 -> 3, 5]
                            Newline+
                                Newline+ <<13, 14>> ws:None [3, 5 -> 4, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
                    Repeat: (Sequence: [Word Token, Newline+], 1, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordc'>>> ws:None [4, 1 -> 4, 6]
                            Newline+
                                Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='wordd'>>> ws:None [5, 1 -> 5, 6]
                            Newline+
                                Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(26, 31), match='worde'>>> ws:None [6, 1 -> 6, 6]
                            Newline+
                                Newline+ <<31, 32>> ws:None [6, 6 -> 7, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert len(parse_mock.method_calls) == 81

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match4(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    12
                    3456
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            26
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
                    Repeat: (Sequence: [Word Token, Newline+], 1, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                            Newline+
                                Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                            Newline+
                                Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='worde'>>> ws:None [5, 1 -> 5, 6]
                            Newline+
                                Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
            """,
        )

        assert result.Iter.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            1) StartStatement, "Repeat: (Sequence: [Word Token, Newline+], 0, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            2) StartStatement, "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 0, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            3) StartStatement, "Word Token", "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 0, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            4) EndStatement, "Word Token" [False], "Sequence: [Word Token, Newline+]" [None], "Repeat: (Sequence: [Word Token, Newline+], 0, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            5) EndStatement, "Sequence: [Word Token, Newline+]" [False], "Repeat: (Sequence: [Word Token, Newline+], 0, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            6) OnInternalStatementAsync, 0, 0
                Repeat: (Sequence: [Word Token, Newline+], 0, None)
                    <No Items>
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    <No Items>
            7) EndStatement, "Repeat: (Sequence: [Word Token, Newline+], 0, None)" [True], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            8) StartStatement, "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            9) StartStatement, "Sequence: [Number Token, Newline+]", "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            10) StartStatement, "Number Token", "Sequence: [Number Token, Newline+]", "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            11) OnInternalStatementAsync, 0, 2
                Number Token
                    Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                Sequence: [Number Token, Newline+]
                    <No Items>
                Repeat: (Sequence: [Number Token, Newline+], 1, None)
                    <No Items>
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
            12) EndStatement, "Number Token" [True], "Sequence: [Number Token, Newline+]" [None], "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            13) StartStatement, "Newline+", "Sequence: [Number Token, Newline+]", "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            14) OnInternalStatementAsync, 2, 3
                Newline+
                    Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                Sequence: [Number Token, Newline+]
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                Repeat: (Sequence: [Number Token, Newline+], 1, None)
                    <No Items>
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
            15) EndStatement, "Newline+" [True], "Sequence: [Number Token, Newline+]" [None], "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            16) OnInternalStatementAsync, 0, 3
                Sequence: [Number Token, Newline+]
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                    Newline+
                        Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                Repeat: (Sequence: [Number Token, Newline+], 1, None)
                    <No Items>
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
            17) EndStatement, "Sequence: [Number Token, Newline+]" [True], "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            18) StartStatement, "Sequence: [Number Token, Newline+]", "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            19) StartStatement, "Number Token", "Sequence: [Number Token, Newline+]", "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            20) OnInternalStatementAsync, 3, 7
                Number Token
                    Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                Sequence: [Number Token, Newline+]
                    <No Items>
                Repeat: (Sequence: [Number Token, Newline+], 1, None)
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                        Newline+
                            Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
            21) EndStatement, "Number Token" [True], "Sequence: [Number Token, Newline+]" [None], "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            22) StartStatement, "Newline+", "Sequence: [Number Token, Newline+]", "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            23) OnInternalStatementAsync, 7, 8
                Newline+
                    Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                Sequence: [Number Token, Newline+]
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                Repeat: (Sequence: [Number Token, Newline+], 1, None)
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                        Newline+
                            Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
            24) EndStatement, "Newline+" [True], "Sequence: [Number Token, Newline+]" [None], "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            25) OnInternalStatementAsync, 3, 8
                Sequence: [Number Token, Newline+]
                    Number Token
                        Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                    Newline+
                        Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                Repeat: (Sequence: [Number Token, Newline+], 1, None)
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                        Newline+
                            Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
            26) EndStatement, "Sequence: [Number Token, Newline+]" [True], "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            27) StartStatement, "Sequence: [Number Token, Newline+]", "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            28) StartStatement, "Number Token", "Sequence: [Number Token, Newline+]", "Repeat: (Sequence: [Number Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            29) EndStatement, "Number Token" [False], "Sequence: [Number Token, Newline+]" [None], "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            30) EndStatement, "Sequence: [Number Token, Newline+]" [False], "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            31) OnInternalStatementAsync, 0, 8
                Repeat: (Sequence: [Number Token, Newline+], 1, None)
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                        Newline+
                            Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                        Newline+
                            Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
            32) EndStatement, "Repeat: (Sequence: [Number Token, Newline+], 1, None)" [True], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            33) StartStatement, "Repeat: (Sequence: [Upper Token, Newline+], 0, 1)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            34) StartStatement, "Sequence: [Upper Token, Newline+]", "Repeat: (Sequence: [Upper Token, Newline+], 0, 1)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            35) StartStatement, "Upper Token", "Sequence: [Upper Token, Newline+]", "Repeat: (Sequence: [Upper Token, Newline+], 0, 1)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            36) EndStatement, "Upper Token" [False], "Sequence: [Upper Token, Newline+]" [None], "Repeat: (Sequence: [Upper Token, Newline+], 0, 1)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            37) EndStatement, "Sequence: [Upper Token, Newline+]" [False], "Repeat: (Sequence: [Upper Token, Newline+], 0, 1)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            38) OnInternalStatementAsync, 8, 8
                Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                    <No Items>
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
            39) EndStatement, "Repeat: (Sequence: [Upper Token, Newline+], 0, 1)" [True], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            40) StartStatement, "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            41) StartStatement, "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            42) StartStatement, "Word Token", "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            43) OnInternalStatementAsync, 8, 13
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                Sequence: [Word Token, Newline+]
                    <No Items>
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    <No Items>
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            44) EndStatement, "Word Token" [True], "Sequence: [Word Token, Newline+]" [None], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            45) StartStatement, "Newline+", "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            46) OnInternalStatementAsync, 13, 14
                Newline+
                    Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                Sequence: [Word Token, Newline+]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    <No Items>
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            47) EndStatement, "Newline+" [True], "Sequence: [Word Token, Newline+]" [None], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            48) OnInternalStatementAsync, 8, 14
                Sequence: [Word Token, Newline+]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                    Newline+
                        Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    <No Items>
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            49) EndStatement, "Sequence: [Word Token, Newline+]" [True], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            50) StartStatement, "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            51) StartStatement, "Word Token", "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            52) OnInternalStatementAsync, 14, 19
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                Sequence: [Word Token, Newline+]
                    <No Items>
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                        Newline+
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            53) EndStatement, "Word Token" [True], "Sequence: [Word Token, Newline+]" [None], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            54) StartStatement, "Newline+", "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            55) OnInternalStatementAsync, 19, 20
                Newline+
                    Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                Sequence: [Word Token, Newline+]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                        Newline+
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            56) EndStatement, "Newline+" [True], "Sequence: [Word Token, Newline+]" [None], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            57) OnInternalStatementAsync, 14, 20
                Sequence: [Word Token, Newline+]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                    Newline+
                        Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                        Newline+
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            58) EndStatement, "Sequence: [Word Token, Newline+]" [True], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            59) StartStatement, "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            60) StartStatement, "Word Token", "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            61) OnInternalStatementAsync, 20, 25
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='worde'>>> ws:None [5, 1 -> 5, 6]
                Sequence: [Word Token, Newline+]
                    <No Items>
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                        Newline+
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                        Newline+
                            Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            62) EndStatement, "Word Token" [True], "Sequence: [Word Token, Newline+]" [None], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            63) StartStatement, "Newline+", "Sequence: [Word Token, Newline+]", "Repeat: (Sequence: [Word Token, Newline+], 1, None)", "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]"
            64) OnInternalStatementAsync, 25, 26
                Newline+
                    Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                Sequence: [Word Token, Newline+]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='worde'>>> ws:None [5, 1 -> 5, 6]
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                        Newline+
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                        Newline+
                            Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            65) EndStatement, "Newline+" [True], "Sequence: [Word Token, Newline+]" [None], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            66) OnInternalStatementAsync, 20, 26
                Sequence: [Word Token, Newline+]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='worde'>>> ws:None [5, 1 -> 5, 6]
                    Newline+
                        Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                        Newline+
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                        Newline+
                            Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            67) EndStatement, "Sequence: [Word Token, Newline+]" [True], "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [None], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            68) OnInternalStatementAsync, 8, 26
                Repeat: (Sequence: [Word Token, Newline+], 1, None)
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                        Newline+
                            Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                        Newline+
                            Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='worde'>>> ws:None [5, 1 -> 5, 6]
                        Newline+
                            Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
            69) EndStatement, "Repeat: (Sequence: [Word Token, Newline+], 1, None)" [True], "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [None]
            70) OnInternalStatementAsync, 0, 26
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        <No Items>
                    Repeat: (Sequence: [Word Token, Newline+], 1, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='wordc'>>> ws:None [3, 1 -> 3, 6]
                            Newline+
                                Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(14, 19), match='wordd'>>> ws:None [4, 1 -> 4, 6]
                            Newline+
                                Newline+ <<19, 20>> ws:None [4, 6 -> 5, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(20, 25), match='worde'>>> ws:None [5, 1 -> 5, 6]
                            Newline+
                                Newline+ <<25, 26>> ws:None [5, 6 -> 6, 1]
            71) EndStatement, "Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch1(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    wordb
                    UPPER
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            12
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                            Newline+
                                Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='wordb'>>> ws:None [2, 1 -> 2, 6]
                            Newline+
                                Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 33

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch2(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    12
                    3456
                    UPPER
                    999
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            14
                Sequence: [Repeat: (Sequence: [Word Token, Newline+], 0, None), Repeat: (Sequence: [Number Token, Newline+], 1, None), Repeat: (Sequence: [Upper Token, Newline+], 0, 1), Repeat: (Sequence: [Word Token, Newline+], 1, None)]
                    Repeat: (Sequence: [Word Token, Newline+], 0, None)
                        <No Items>
                    Repeat: (Sequence: [Number Token, Newline+], 1, None)
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(0, 2), match='12'>>> ws:None [1, 1 -> 1, 3]
                            Newline+
                                Newline+ <<2, 3>> ws:None [1, 3 -> 2, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(3, 7), match='3456'>>> ws:None [2, 1 -> 2, 5]
                            Newline+
                                Newline+ <<7, 8>> ws:None [2, 5 -> 3, 1]
                    Repeat: (Sequence: [Upper Token, Newline+], 0, 1)
                        Sequence: [Upper Token, Newline+]
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(8, 13), match='UPPER'>>> ws:None [3, 1 -> 3, 6]
                            Newline+
                                Newline+ <<13, 14>> ws:None [3, 6 -> 4, 1]
                    Repeat: (Sequence: [Word Token, Newline+], 1, None)
                        Sequence: [Word Token, Newline+]
                            Word Token
                                <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 52

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EarlyTermination(self, parse_mock):
        parse_mock.OnInternalStatementAsync = CoroutineMock(
            side_effect=[True, True, True, True, False],
        )

        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    wordb
                    12
                    3456
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        assert result is None

# ----------------------------------------------------------------------
class TestRepeatSimilarStatements(object):
    # Ensure that the first statement doesn't eat the word so that it isn't available to the
    # second statement.
    _statement                              = CreateStatement(
        item=[
            StatementItem(
                name="Word & Number",
                item=[_word_token, _number_token],
                arity="*",
            ),
            StatementItem(
                item=_word_token,
                arity="?",
            ),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_LargeMatch(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("word 123"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            8
                Sequence: [Repeat: (Word & Number, 0, None), Repeat: (Word Token, 0, 1)]
                    Repeat: (Word & Number, 0, None)
                        Word & Number
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(5, 8), match='123'>>> ws:(4, 5) [1, 6 -> 1, 9]
                    Repeat: (Word Token, 0, 1)
                        <No Items>
            """,
        )

        # assert result.Iter.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SmallMatch(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("word"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            4
                Sequence: [Repeat: (Word & Number, 0, None), Repeat: (Word Token, 0, 1)]
                    Repeat: (Word & Number, 0, None)
                        <No Items>
                    Repeat: (Word Token, 0, 1)
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='word'>>> ws:None [1, 1 -> 1, 5]
            """,
        )

        # assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
class TestNamedStatements(object):
    _word_line_statement                    = CreateStatement(
        name="Word Line",
        item=[_word_token, NewlineToken()],
    )

    _statement                              = CreateStatement(
        name="__Statement__",
        item=[
            StatementItem(name="__Dynamic__", item=DynamicStatements.Statements),
            StatementItem(
                name="__Or__",
                item=(
                    _word_line_statement,
                    StatementItem(name="Upper Line", item=[_upper_token, NewlineToken()]),
                ),
            ),
            StatementItem(name="__Repeat__", item=[_number_token, NewlineToken()], arity=(2, 2)),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.fixture
    def modified_parse_mock(self, parse_mock):
        parse_mock.GetDynamicStatements.side_effect = lambda unique_id, value: [self._word_line_statement]

        return parse_mock

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, modified_parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    WORDB
                    123
                    456
                    """,
                ),
            ),
            modified_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            20
                __Statement__
                    __Dynamic__
                        Or: {Word Line}
                            Word Line
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Newline+
                                    Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                    __Or__
                        Upper Line
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='WORDB'>>> ws:None [2, 1 -> 2, 6]
                            Newline+
                                Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                    Repeat: (__Repeat__, 2, 2)
                        __Repeat__
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [3, 1 -> 3, 4]
                            Newline+
                                Newline+ <<15, 16>> ws:None [3, 4 -> 4, 1]
                        __Repeat__
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='456'>>> ws:None [4, 1 -> 4, 4]
                            Newline+
                                Newline+ <<19, 20>> ws:None [4, 4 -> 5, 1]
            """,
        )

        assert result.Iter.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, modified_parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    WORDB
                    123
                    """,
                ),
            ),
            modified_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            False
            16
                __Statement__
                    __Dynamic__
                        Or: {Word Line}
                            Word Line
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                                Newline+
                                    Newline+ <<5, 6>> ws:None [1, 6 -> 2, 1]
                    __Or__
                        Upper Line
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='WORDB'>>> ws:None [2, 1 -> 2, 6]
                            Newline+
                                Newline+ <<11, 12>> ws:None [2, 6 -> 3, 1]
                    Repeat: (__Repeat__, 2, 2)
                        __Repeat__
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(12, 15), match='123'>>> ws:None [3, 1 -> 3, 4]
                            Newline+
                                Newline+ <<15, 16>> ws:None [3, 4 -> 4, 1]
            """,
        )

# ----------------------------------------------------------------------
class TestComments(object):
    _multiline_statement                    = CreateStatement(
        StatementItem(
            name="Multiline",
            item=[
                [_word_token, NewlineToken()],
                [_upper_token, NewlineToken()],
                [_number_token, NewlineToken()],
            ],
            arity="+",
        ),
    )

    _indent_statement                       = CreateStatement(
        name="Indent",
        item=[
            _word_token,
            RegexToken("Colon", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            [_upper_token, NewlineToken()],
            [_number_token, NewlineToken()],
            DedentToken(),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Multiline(self, parse_mock):
        result = await self._multiline_statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    one # Comment 1
                    TWO
                    3
                    four
                    FIVE                    # Comment 5
                    66
                    seven
                    EIGHT
                    999     # Comment 9
                    ten      # Comment 10
                    ELEVEN   # Comment 11
                    12       # Comment 12
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            164
                Repeat: (Multiline, 1, None)
                    Multiline
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                            Comment <<Regex: <_sre.SRE_Match object; span=(4, 15), match='# Comment 1'>>> ws:(3, 4) !Ignored! [1, 5 -> 1, 16]
                            Newline+
                                Newline+ <<15, 16>> ws:None [1, 16 -> 2, 1]
                        Sequence: [Upper Token, Newline+]
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(16, 19), match='TWO'>>> ws:None [2, 1 -> 2, 4]
                            Newline+
                                Newline+ <<19, 20>> ws:None [2, 4 -> 3, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(20, 21), match='3'>>> ws:None [3, 1 -> 3, 2]
                            Newline+
                                Newline+ <<21, 22>> ws:None [3, 2 -> 4, 1]
                    Multiline
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(22, 26), match='four'>>> ws:None [4, 1 -> 4, 5]
                            Newline+
                                Newline+ <<26, 27>> ws:None [4, 5 -> 5, 1]
                        Sequence: [Upper Token, Newline+]
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(27, 31), match='FIVE'>>> ws:None [5, 1 -> 5, 5]
                            Comment <<Regex: <_sre.SRE_Match object; span=(51, 62), match='# Comment 5'>>> ws:(31, 51) !Ignored! [5, 25 -> 5, 36]
                            Newline+
                                Newline+ <<62, 63>> ws:None [5, 36 -> 6, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(63, 65), match='66'>>> ws:None [6, 1 -> 6, 3]
                            Newline+
                                Newline+ <<65, 66>> ws:None [6, 3 -> 7, 1]
                    Multiline
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(66, 71), match='seven'>>> ws:None [7, 1 -> 7, 6]
                            Newline+
                                Newline+ <<71, 72>> ws:None [7, 6 -> 8, 1]
                        Sequence: [Upper Token, Newline+]
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(72, 77), match='EIGHT'>>> ws:None [8, 1 -> 8, 6]
                            Newline+
                                Newline+ <<77, 78>> ws:None [8, 6 -> 9, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(78, 81), match='999'>>> ws:None [9, 1 -> 9, 4]
                            Comment <<Regex: <_sre.SRE_Match object; span=(86, 97), match='# Comment 9'>>> ws:(81, 86) !Ignored! [9, 9 -> 9, 20]
                            Newline+
                                Newline+ <<97, 98>> ws:None [9, 20 -> 10, 1]
                    Multiline
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(98, 101), match='ten'>>> ws:None [10, 1 -> 10, 4]
                            Comment <<Regex: <_sre.SRE_Match object; span=(107, 119), match='# Comment 10'>>> ws:(101, 107) !Ignored! [10, 10 -> 10, 22]
                            Newline+
                                Newline+ <<119, 120>> ws:None [10, 22 -> 11, 1]
                        Sequence: [Upper Token, Newline+]
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(120, 126), match='ELEVEN'>>> ws:None [11, 1 -> 11, 7]
                            Comment <<Regex: <_sre.SRE_Match object; span=(129, 141), match='# Comment 11'>>> ws:(126, 129) !Ignored! [11, 10 -> 11, 22]
                            Newline+
                                Newline+ <<141, 142>> ws:None [11, 22 -> 12, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(142, 144), match='12'>>> ws:None [12, 1 -> 12, 3]
                            Comment <<Regex: <_sre.SRE_Match object; span=(151, 163), match='# Comment 12'>>> ws:(144, 151) !Ignored! [12, 10 -> 12, 22]
                            Newline+
                                Newline+ <<163, 164>> ws:None [12, 22 -> 13, 1]
            """,
        )

        assert result.Iter.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Indent(self, parse_mock):
        iterator = CreateIterator(
            textwrap.dedent(
                """\
                one:  # Comment 1
                    TWO
                    3
                four:
                    FIVE # Comment 5
                    66
                seven:
                    EIGHT
                    999                     # Comment 9
                ten:            # Comment 10
                    ELEVEN      # Comment 11
                    12          # Comment 12
                """,
            ),
        )

        # 1-3
        result = await self._indent_statement.ParseAsync(["root"], iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            32
                Indent
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Colon
                        Colon <<Regex: <_sre.SRE_Match object; span=(3, 4), match=':'>>> ws:None [1, 4 -> 1, 5]
                    Comment <<Regex: <_sre.SRE_Match object; span=(6, 17), match='# Comment 1'>>> ws:(4, 6) !Ignored! [1, 7 -> 1, 18]
                    Newline+
                        Newline+ <<17, 18>> ws:None [1, 18 -> 2, 1]
                    Indent
                        Indent <<18, 22, (4)>> ws:None [2, 1 -> 2, 5]
                    Sequence: [Upper Token, Newline+]
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(22, 25), match='TWO'>>> ws:None [2, 5 -> 2, 8]
                        Newline+
                            Newline+ <<25, 26>> ws:None [2, 8 -> 3, 1]
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(30, 31), match='3'>>> ws:None [3, 5 -> 3, 6]
                        Newline+
                            Newline+ <<31, 32>> ws:None [3, 6 -> 4, 1]
                    Dedent
                        Dedent <<>> ws:None [4, 1 -> 4, 1]
            """,
        )

        iterator = result.Iter

        # 4-6
        result = await self._indent_statement.ParseAsync(["root"], iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            66
                Indent
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(32, 36), match='four'>>> ws:None [4, 1 -> 4, 5]
                    Colon
                        Colon <<Regex: <_sre.SRE_Match object; span=(36, 37), match=':'>>> ws:None [4, 5 -> 4, 6]
                    Newline+
                        Newline+ <<37, 38>> ws:None [4, 6 -> 5, 1]
                    Indent
                        Indent <<38, 42, (4)>> ws:None [5, 1 -> 5, 5]
                    Sequence: [Upper Token, Newline+]
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(42, 46), match='FIVE'>>> ws:None [5, 5 -> 5, 9]
                        Comment <<Regex: <_sre.SRE_Match object; span=(47, 58), match='# Comment 5'>>> ws:(46, 47) !Ignored! [5, 10 -> 5, 21]
                        Newline+
                            Newline+ <<58, 59>> ws:None [5, 21 -> 6, 1]
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(63, 65), match='66'>>> ws:None [6, 5 -> 6, 7]
                        Newline+
                            Newline+ <<65, 66>> ws:None [6, 7 -> 7, 1]
                    Dedent
                        Dedent <<>> ws:None [7, 1 -> 7, 1]
            """,
        )

        iterator = result.Iter

        # 7-9
        result = await self._indent_statement.ParseAsync(["root"], iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            123
                Indent
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(66, 71), match='seven'>>> ws:None [7, 1 -> 7, 6]
                    Colon
                        Colon <<Regex: <_sre.SRE_Match object; span=(71, 72), match=':'>>> ws:None [7, 6 -> 7, 7]
                    Newline+
                        Newline+ <<72, 73>> ws:None [7, 7 -> 8, 1]
                    Indent
                        Indent <<73, 77, (4)>> ws:None [8, 1 -> 8, 5]
                    Sequence: [Upper Token, Newline+]
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(77, 82), match='EIGHT'>>> ws:None [8, 5 -> 8, 10]
                        Newline+
                            Newline+ <<82, 83>> ws:None [8, 10 -> 9, 1]
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(87, 90), match='999'>>> ws:None [9, 5 -> 9, 8]
                        Comment <<Regex: <_sre.SRE_Match object; span=(111, 122), match='# Comment 9'>>> ws:(90, 111) !Ignored! [9, 29 -> 9, 40]
                        Newline+
                            Newline+ <<122, 123>> ws:None [9, 40 -> 10, 1]
                    Dedent
                        Dedent <<>> ws:None [10, 1 -> 10, 1]
            """,
        )

        iterator = result.Iter

        # 10-12
        result = await self._indent_statement.ParseAsync(["root"], iterator, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            True
            210
                Indent
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(123, 126), match='ten'>>> ws:None [10, 1 -> 10, 4]
                    Colon
                        Colon <<Regex: <_sre.SRE_Match object; span=(126, 127), match=':'>>> ws:None [10, 4 -> 10, 5]
                    Comment <<Regex: <_sre.SRE_Match object; span=(139, 151), match='# Comment 10'>>> ws:(127, 139) !Ignored! [10, 17 -> 10, 29]
                    Newline+
                        Newline+ <<151, 152>> ws:None [10, 29 -> 11, 1]
                    Indent
                        Indent <<152, 156, (4)>> ws:None [11, 1 -> 11, 5]
                    Sequence: [Upper Token, Newline+]
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(156, 162), match='ELEVEN'>>> ws:None [11, 5 -> 11, 11]
                        Comment <<Regex: <_sre.SRE_Match object; span=(168, 180), match='# Comment 11'>>> ws:(162, 168) !Ignored! [11, 17 -> 11, 29]
                        Newline+
                            Newline+ <<180, 181>> ws:None [11, 29 -> 12, 1]
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(185, 187), match='12'>>> ws:None [12, 5 -> 12, 7]
                        Comment <<Regex: <_sre.SRE_Match object; span=(197, 209), match='# Comment 12'>>> ws:(187, 197) !Ignored! [12, 17 -> 12, 29]
                        Newline+
                            Newline+ <<209, 210>> ws:None [12, 29 -> 13, 1]
                    Dedent
                        Dedent <<>> ws:None [13, 1 -> 13, 1]
            """,
        )

        iterator = result.Iter

        assert result.Iter.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_StandAlone(self, parse_mock):
        result = await self._multiline_statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    # one
                    one     # After one

                    # TWO

                    TWO     # After TWO

                            # 3
                    3       # After 3
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            85
                Repeat: (Multiline, 1, None)
                    Multiline
                        Comment <<Regex: <_sre.SRE_Match object; span=(0, 5), match='# one'>>> ws:None !Ignored! [1, 1 -> 1, 6]
                        Newline+ <<5, 6>> ws:None !Ignored! [1, 6 -> 2, 1]
                        Sequence: [Word Token, Newline+]
                            Word Token
                                Word Token <<Regex: <_sre.SRE_Match object; span=(6, 9), match='one'>>> ws:None [2, 1 -> 2, 4]
                            Comment <<Regex: <_sre.SRE_Match object; span=(14, 25), match='# After one'>>> ws:(9, 14) !Ignored! [2, 9 -> 2, 20]
                            Newline+
                                Newline+ <<25, 27>> ws:None [2, 20 -> 4, 1]
                        Comment <<Regex: <_sre.SRE_Match object; span=(27, 32), match='# TWO'>>> ws:None !Ignored! [4, 1 -> 4, 6]
                        Newline+ <<32, 34>> ws:None !Ignored! [4, 6 -> 6, 1]
                        Sequence: [Upper Token, Newline+]
                            Upper Token
                                Upper Token <<Regex: <_sre.SRE_Match object; span=(34, 37), match='TWO'>>> ws:None [6, 1 -> 6, 4]
                            Comment <<Regex: <_sre.SRE_Match object; span=(42, 53), match='# After TWO'>>> ws:(37, 42) !Ignored! [6, 9 -> 6, 20]
                            Newline+
                                Newline+ <<53, 55>> ws:None [6, 20 -> 8, 1]
                        Comment <<Regex: <_sre.SRE_Match object; span=(63, 66), match='# 3'>>> ws:(55, 63) !Ignored! [8, 9 -> 8, 12]
                        Newline+ <<66, 67>> ws:None !Ignored! [8, 12 -> 9, 1]
                        Sequence: [Number Token, Newline+]
                            Number Token
                                Number Token <<Regex: <_sre.SRE_Match object; span=(67, 68), match='3'>>> ws:None [9, 1 -> 9, 2]
                            Comment <<Regex: <_sre.SRE_Match object; span=(75, 84), match='# After 3'>>> ws:(68, 75) !Ignored! [9, 9 -> 9, 18]
                            Newline+
                                Newline+ <<84, 85>> ws:None [9, 18 -> 10, 1]
            """,
        )

        assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
class TestRecursiveOrStatements(object):
    _statement                              = CreateStatement(
        name="Recursive Statement",
        item=[
            _lpar_token,
            (_word_token, None),
            _rpar_token,
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoRecursion(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("( hello )"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Recursive Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Or: {Word Token, Recursive Statement}
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(2, 7), match='hello'>>> ws:(1, 2) [1, 3 -> 1, 8]
                    rpar
                        rpar <<Regex: <_sre.SRE_Match object; span=(8, 9), match=')'>>> ws:(7, 8) [1, 9 -> 1, 10]
            """,
        )

        # assert result.Iter.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleRecursion(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("((hello))"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            9
                Recursive Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Or: {Word Token, Recursive Statement}
                        Recursive Statement
                            lpar
                                lpar <<Regex: <_sre.SRE_Match object; span=(1, 2), match='('>>> ws:None [1, 2 -> 1, 3]
                            Or: {Word Token, Recursive Statement}
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(2, 7), match='hello'>>> ws:None [1, 3 -> 1, 8]
                            rpar
                                rpar <<Regex: <_sre.SRE_Match object; span=(7, 8), match=')'>>> ws:None [1, 8 -> 1, 9]
                    rpar
                        rpar <<Regex: <_sre.SRE_Match object; span=(8, 9), match=')'>>> ws:None [1, 9 -> 1, 10]
            """,
        )

        # assert result.Iter.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_DoubleRecursion(self, parse_mock):
        result = await self._statement.ParseAsync(["root"], CreateIterator("( ( ( hello)))"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            True
            14
                Recursive Statement
                    lpar
                        lpar <<Regex: <_sre.SRE_Match object; span=(0, 1), match='('>>> ws:None [1, 1 -> 1, 2]
                    Or: {Word Token, Recursive Statement}
                        Recursive Statement
                            lpar
                                lpar <<Regex: <_sre.SRE_Match object; span=(2, 3), match='('>>> ws:(1, 2) [1, 3 -> 1, 4]
                            Or: {Word Token, Recursive Statement}
                                Recursive Statement
                                    lpar
                                        lpar <<Regex: <_sre.SRE_Match object; span=(4, 5), match='('>>> ws:(3, 4) [1, 5 -> 1, 6]
                                    Or: {Word Token, Recursive Statement}
                                        Word Token
                                            Word Token <<Regex: <_sre.SRE_Match object; span=(6, 11), match='hello'>>> ws:(5, 6) [1, 7 -> 1, 12]
                                    rpar
                                        rpar <<Regex: <_sre.SRE_Match object; span=(11, 12), match=')'>>> ws:None [1, 12 -> 1, 13]
                            rpar
                                rpar <<Regex: <_sre.SRE_Match object; span=(12, 13), match=')'>>> ws:None [1, 13 -> 1, 14]
                    rpar
                        rpar <<Regex: <_sre.SRE_Match object; span=(13, 14), match=')'>>> ws:None [1, 14 -> 1, 15]
            """,
        )

        # assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
class TestRecursiveRepeatStatement(object):
    _statement                              = CreateStatement(
        name="Recursive Statement",
        item=[
            [_number_token, NewlineToken()],
            (
                StatementItem(None, arity=(1, 2)),
                [_word_token, NewlineToken()]
            ),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    123
                    456
                    789
                    helloa
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            19
                Recursive Statement
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='123'>>> ws:None [1, 1 -> 1, 4]
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: {Repeat: (Recursive Statement, 1, 2), Sequence: [Word Token, Newline+]}
                        Repeat: (Recursive Statement, 1, 2)
                            Recursive Statement
                                Sequence: [Number Token, Newline+]
                                    Number Token
                                        Number Token <<Regex: <_sre.SRE_Match object; span=(4, 7), match='456'>>> ws:None [2, 1 -> 2, 4]
                                    Newline+
                                        Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
                                Or: {Repeat: (Recursive Statement, 1, 2), Sequence: [Word Token, Newline+]}
                                    Repeat: (Recursive Statement, 1, 2)
                                        Recursive Statement
                                            Sequence: [Number Token, Newline+]
                                                Number Token
                                                    Number Token <<Regex: <_sre.SRE_Match object; span=(8, 11), match='789'>>> ws:None [3, 1 -> 3, 4]
                                                Newline+
                                                    Newline+ <<11, 12>> ws:None [3, 4 -> 4, 1]
                                            Or: {Repeat: (Recursive Statement, 1, 2), Sequence: [Word Token, Newline+]}
                                                Sequence: [Word Token, Newline+]
                                                    Word Token
                                                        Word Token <<Regex: <_sre.SRE_Match object; span=(12, 18), match='helloa'>>> ws:None [4, 1 -> 4, 7]
                                                    Newline+
                                                        Newline+ <<18, 19>> ws:None [4, 7 -> 5, 1]
            """,
        )

        assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
class TestRecursiveSequenceStatement(object):
    _statement                              = CreateStatement(
        [
            [_number_token, NewlineToken()],
            [_upper_token, NewlineToken()],
            (
                None,
                [RegexToken("Delimiter", re.compile(r"---")), NewlineToken()],
            ),
            [_word_token, NewlineToken()],
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await self._statement.ParseAsync(
            ["root"],
            CreateIterator(
                textwrap.dedent(
                    """\
                    123
                    UPPERA
                    456
                    UPPERB
                    789
                    UPPERC
                    ---
                    worda
                    wordb
                    wordc
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            True
            55
                Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Recursive, Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]], Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]]
                    Sequence: [Number Token, Newline+]
                        Number Token
                            Number Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='123'>>> ws:None [1, 1 -> 1, 4]
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Sequence: [Upper Token, Newline+]
                        Upper Token
                            Upper Token <<Regex: <_sre.SRE_Match object; span=(4, 10), match='UPPERA'>>> ws:None [2, 1 -> 2, 7]
                        Newline+
                            Newline+ <<10, 11>> ws:None [2, 7 -> 3, 1]
                    Or: {Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Recursive, Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]], Sequence: [Delimiter, Newline+]}
                        Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Recursive, Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]], Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]]
                            Sequence: [Number Token, Newline+]
                                Number Token
                                    Number Token <<Regex: <_sre.SRE_Match object; span=(11, 14), match='456'>>> ws:None [3, 1 -> 3, 4]
                                Newline+
                                    Newline+ <<14, 15>> ws:None [3, 4 -> 4, 1]
                            Sequence: [Upper Token, Newline+]
                                Upper Token
                                    Upper Token <<Regex: <_sre.SRE_Match object; span=(15, 21), match='UPPERB'>>> ws:None [4, 1 -> 4, 7]
                                Newline+
                                    Newline+ <<21, 22>> ws:None [4, 7 -> 5, 1]
                            Or: {Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Recursive, Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]], Sequence: [Delimiter, Newline+]}
                                Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Recursive, Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]], Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]]
                                    Sequence: [Number Token, Newline+]
                                        Number Token
                                            Number Token <<Regex: <_sre.SRE_Match object; span=(22, 25), match='789'>>> ws:None [5, 1 -> 5, 4]
                                        Newline+
                                            Newline+ <<25, 26>> ws:None [5, 4 -> 6, 1]
                                    Sequence: [Upper Token, Newline+]
                                        Upper Token
                                            Upper Token <<Regex: <_sre.SRE_Match object; span=(26, 32), match='UPPERC'>>> ws:None [6, 1 -> 6, 7]
                                        Newline+
                                            Newline+ <<32, 33>> ws:None [6, 7 -> 7, 1]
                                    Or: {Sequence: [Sequence: [Number Token, Newline+], Sequence: [Upper Token, Newline+], Or: {Recursive, Sequence: [Delimiter, Newline+]}, Sequence: [Word Token, Newline+]], Sequence: [Delimiter, Newline+]}
                                        Sequence: [Delimiter, Newline+]
                                            Delimiter
                                                Delimiter <<Regex: <_sre.SRE_Match object; span=(33, 36), match='---'>>> ws:None [7, 1 -> 7, 4]
                                            Newline+
                                                Newline+ <<36, 37>> ws:None [7, 4 -> 8, 1]
                                    Sequence: [Word Token, Newline+]
                                        Word Token
                                            Word Token <<Regex: <_sre.SRE_Match object; span=(37, 42), match='worda'>>> ws:None [8, 1 -> 8, 6]
                                        Newline+
                                            Newline+ <<42, 43>> ws:None [8, 6 -> 9, 1]
                            Sequence: [Word Token, Newline+]
                                Word Token
                                    Word Token <<Regex: <_sre.SRE_Match object; span=(43, 48), match='wordb'>>> ws:None [9, 1 -> 9, 6]
                                Newline+
                                    Newline+ <<48, 49>> ws:None [9, 6 -> 10, 1]
                    Sequence: [Word Token, Newline+]
                        Word Token
                            Word Token <<Regex: <_sre.SRE_Match object; span=(49, 54), match='wordc'>>> ws:None [10, 1 -> 10, 6]
                        Newline+
                            Newline+ <<54, 55>> ws:None [10, 6 -> 11, 1]
            """,
        )

        assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_IgnoreWhitespace(parse_mock):
    statement = CreateStatement(
        name="Statement",
        item=[
            PushIgnoreWhitespaceControlToken(),
            _word_token,
            _word_token,
            PopIgnoreWhitespaceControlToken(),
        ],
    )

    result = await statement.ParseAsync(
        ["root"],
        CreateIterator(
            textwrap.dedent(
                """\



                            worda

                    wordb

                """,
            ),
        ),
        parse_mock,
    )

    assert str(result) == textwrap.dedent(
        """\
        True
        25
            Statement
                Newline+ <<0, 3>> ws:None !Ignored! [1, 1 -> 4, 1]
                Indent <<3, 11, (8)>> ws:None !Ignored! [4, 1 -> 4, 9]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(11, 16), match='worda'>>> ws:None [4, 9 -> 4, 14]
                Newline+ <<16, 18>> ws:None !Ignored! [4, 14 -> 6, 1]
                Dedent <<>> ws:None !Ignored! [6, 1 -> 6, 1]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(18, 23), match='wordb'>>> ws:None [6, 1 -> 6, 6]
                Newline+ <<23, 25>> ws:None !Ignored! [6, 6 -> 8, 1]
        """,
    )

    assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_IgnoreWhitespaceNestedStatement(parse_mock):
    statement = CreateStatement(
        name="Statement",
        item=[
            _word_token,
            NewlineToken(),
            CreateStatement(
                name="Nested",
                item=[
                    PushIgnoreWhitespaceControlToken(),
                    _word_token,
                    _word_token,
                    PopIgnoreWhitespaceControlToken(),
                ],
            ),
            _word_token,
            NewlineToken(),
        ],
    )

    result = await statement.ParseAsync(
        ["root"],
        CreateIterator(
            textwrap.dedent(
                """\
                worda


                        wordb
                            wordc

                wordd
                """,
            ),
        ),
        parse_mock,
    )

    assert str(result) == textwrap.dedent(
        """\
        True
        47
            Statement
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 5), match='worda'>>> ws:None [1, 1 -> 1, 6]
                Newline+
                    Newline+ <<5, 8>> ws:None [1, 6 -> 4, 1]
                Nested
                    Indent <<8, 16, (8)>> ws:None !Ignored! [4, 1 -> 4, 9]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='wordb'>>> ws:None [4, 9 -> 4, 14]
                    Newline+ <<21, 22>> ws:None !Ignored! [4, 14 -> 5, 1]
                    Indent <<22, 34, (12)>> ws:None !Ignored! [5, 1 -> 5, 13]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(34, 39), match='wordc'>>> ws:None [5, 13 -> 5, 18]
                    Newline+ <<39, 41>> ws:None !Ignored! [5, 18 -> 7, 1]
                    Dedent <<>> ws:None !Ignored! [7, 1 -> 7, 1]
                    Dedent <<>> ws:None !Ignored! [7, 1 -> 7, 1]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(41, 46), match='wordd'>>> ws:None [7, 1 -> 7, 6]
                Newline+
                    Newline+ <<46, 47>> ws:None [7, 6 -> 8, 1]
        """,
    )

    assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_IgnoreWhitespaceNestedStatementWithDedents(parse_mock):
    statement = CreateStatement(
        name="Statement",
        item=[
            _word_token,
            RegexToken("':'", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            CreateStatement(
                name="Nested",
                item=[
                    PushIgnoreWhitespaceControlToken(),
                    _word_token,
                    _word_token,
                    PopIgnoreWhitespaceControlToken(),
                ],
            ),
            _word_token,
            NewlineToken(),
            DedentToken(),
            _word_token,
            NewlineToken(),
        ],
    )

    result = await statement.ParseAsync(
        ["root"],
        CreateIterator(
            textwrap.dedent(
                """\
                newscope:


                    worda
                        wordb

                    wordc
                wordd
                """,
            ),
        ),
        parse_mock,
    )

    assert str(result) == textwrap.dedent(
        """\
        True
        53
            Statement
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 8), match='newscope'>>> ws:None [1, 1 -> 1, 9]
                ':'
                    ':' <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                Newline+
                    Newline+ <<9, 12>> ws:None [1, 10 -> 4, 1]
                Indent
                    Indent <<12, 16, (4)>> ws:None [4, 1 -> 4, 5]
                Nested
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='worda'>>> ws:None [4, 5 -> 4, 10]
                    Newline+ <<21, 22>> ws:None !Ignored! [4, 10 -> 5, 1]
                    Indent <<22, 30, (8)>> ws:None !Ignored! [5, 1 -> 5, 9]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(30, 35), match='wordb'>>> ws:None [5, 9 -> 5, 14]
                    Newline+ <<35, 37>> ws:None !Ignored! [5, 14 -> 7, 1]
                    Dedent <<>> ws:None !Ignored! [7, 1 -> 7, 5]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(41, 46), match='wordc'>>> ws:None [7, 5 -> 7, 10]
                Newline+
                    Newline+ <<46, 47>> ws:None [7, 10 -> 8, 1]
                Dedent
                    Dedent <<>> ws:None [8, 1 -> 8, 1]
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(47, 52), match='wordd'>>> ws:None [8, 1 -> 8, 6]
                Newline+
                    Newline+ <<52, 53>> ws:None [8, 6 -> 9, 1]
        """,
    )

    assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_IgnoreWhitespaceNestedStatementEndWithDedents(parse_mock):
    statement = CreateStatement(
        name="Statement",
        item=[
            _word_token,
            RegexToken("':'", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            CreateStatement(
                name="Nested",
                item=[
                    PushIgnoreWhitespaceControlToken(),
                    _word_token,
                    _word_token,
                    PopIgnoreWhitespaceControlToken(),
                ],
            ),
            DedentToken(),
        ],
    )

    result = await statement.ParseAsync(
        ["root"],
        CreateIterator(
            textwrap.dedent(
                """\
                newscope:


                    worda
                        wordb


                """,
            ),
        ),
        parse_mock,
    )

    assert str(result) == textwrap.dedent(
        """\
        True
        38
            Statement
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 8), match='newscope'>>> ws:None [1, 1 -> 1, 9]
                ':'
                    ':' <<Regex: <_sre.SRE_Match object; span=(8, 9), match=':'>>> ws:None [1, 9 -> 1, 10]
                Newline+
                    Newline+ <<9, 12>> ws:None [1, 10 -> 4, 1]
                Indent
                    Indent <<12, 16, (4)>> ws:None [4, 1 -> 4, 5]
                Nested
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(16, 21), match='worda'>>> ws:None [4, 5 -> 4, 10]
                    Newline+ <<21, 22>> ws:None !Ignored! [4, 10 -> 5, 1]
                    Indent <<22, 30, (8)>> ws:None !Ignored! [5, 1 -> 5, 9]
                    Word Token
                        Word Token <<Regex: <_sre.SRE_Match object; span=(30, 35), match='wordb'>>> ws:None [5, 9 -> 5, 14]
                    Newline+ <<35, 38>> ws:None !Ignored! [5, 14 -> 8, 1]
                    Dedent <<>> ws:None !Ignored! [8, 1 -> 8, 1]
                Dedent
                    Dedent <<>> ws:None [8, 1 -> 8, 1]
        """,
    )

    assert result.Iter.AtEnd()

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_NestedStatement(parse_mock):
    statement = CreateStatement(
        name="Statement",
        item=[TokenStatement(_word_token),],
    )

    result = await statement.ParseAsync(["root"], CreateIterator("test"), parse_mock)

    assert str(result) == textwrap.dedent(
        """\
        True
        4
            Statement
                Word Token
                    Word Token <<Regex: <_sre.SRE_Match object; span=(0, 4), match='test'>>> ws:None [1, 1 -> 1, 5]
        """,
    )

    # assert result.Iter.AtEnd()
