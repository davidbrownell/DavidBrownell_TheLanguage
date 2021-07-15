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
    @pytest.mark.asyncio
    async def test_MatchSingleLine(self, parse_mock):
        result = await self._statement.ParseAsync(
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
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartStatement, "Repeat: (Or: {Word, Newline+}, 2, 4)"
            1) StartStatement, "Or: {Word, Newline+}", "Repeat: (Or: {Word, Newline+}, 2, 4)"
            2) StartStatement, "Word", "Or: {Word, Newline+}", "Repeat: (Or: {Word, Newline+}, 2, 4)"
            3) OnInternalStatementAsync, 0, 3
                Word
                    Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Or: {Word, Newline+}
                    <No Items>
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    <No Items>
            4) EndStatement, "Word" [True], "Or: {Word, Newline+}" [None], "Repeat: (Or: {Word, Newline+}, 2, 4)" [None]
            5) StartStatement, "Newline+", "Or: {Word, Newline+}", "Repeat: (Or: {Word, Newline+}, 2, 4)"
            6) EndStatement, "Newline+" [False], "Or: {Word, Newline+}" [None], "Repeat: (Or: {Word, Newline+}, 2, 4)" [None]
            7) OnInternalStatementAsync, 0, 3
                Or: {Word, Newline+}
                    Word
                        Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    <No Items>
            8) EndStatement, "Or: {Word, Newline+}" [True], "Repeat: (Or: {Word, Newline+}, 2, 4)" [None]
            9) StartStatement, "Or: {Word, Newline+}", "Repeat: (Or: {Word, Newline+}, 2, 4)"
            10) StartStatement, "Word", "Or: {Word, Newline+}", "Repeat: (Or: {Word, Newline+}, 2, 4)"
            11) EndStatement, "Word" [False], "Or: {Word, Newline+}" [None], "Repeat: (Or: {Word, Newline+}, 2, 4)" [None]
            12) StartStatement, "Newline+", "Or: {Word, Newline+}", "Repeat: (Or: {Word, Newline+}, 2, 4)"
            13) OnInternalStatementAsync, 3, 4
                Newline+
                    Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Or: {Word, Newline+}
                    Word
                        <No Data>
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
            14) EndStatement, "Newline+" [True], "Or: {Word, Newline+}" [None], "Repeat: (Or: {Word, Newline+}, 2, 4)" [None]
            15) OnInternalStatementAsync, 3, 4
                Or: {Word, Newline+}
                    Newline+
                        Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
            16) EndStatement, "Or: {Word, Newline+}" [True], "Repeat: (Or: {Word, Newline+}, 2, 4)" [None]
            17) OnInternalStatementAsync, 0, 4
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
            18) EndStatement, "Repeat: (Or: {Word, Newline+}, 2, 4)" [True]
            """,
        )

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchTwoLines(self, parse_mock):
        result = await self._statement.ParseAsync(
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
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 35

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchThreeLines(self, parse_mock):
        result = await self._statement.ParseAsync(
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
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            """,
        )

        assert len(parse_mock.method_calls) == 35

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        result = await self._statement.ParseAsync(
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
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    Or: {Word, Newline+}
                        Word
                            <No Data>
                        Newline+
                            <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 8

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_PartialMatch(self, parse_mock):
        result = await self._statement.ParseAsync(
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
                Repeat: (Or: {Word, Newline+}, 2, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='abc'>>> ws:None [1, 1 -> 1, 4]
                    Or: {Word, Newline+}
                        Word
                            <No Data>
                        Newline+
                            <No Data>
            """,
        )

        assert len(parse_mock.method_calls) == 16

        assert list(result.Data.Enum()) == [
            (self._statement, result.Data.Data),
        ]

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactMatch(self, parse_mock):
        result = await self._exact_statement.ParseAsync(
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
                Repeat: (Or: {Word, Newline+}, 4, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactLimitedMatch(self, parse_mock):
        result = await self._exact_statement.ParseAsync(
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
                Repeat: (Or: {Word, Newline+}, 4, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<3, 4>> ws:None [1, 4 -> 2, 1]
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(4, 7), match='two'>>> ws:None [2, 1 -> 2, 4]
                    Or: {Word, Newline+}
                        Newline+
                            Newline+ <<7, 8>> ws:None [2, 4 -> 3, 1]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactNoMatch(self, parse_mock):
        result = await self._exact_statement.ParseAsync(CreateIterator("one"), parse_mock)

        assert str(result) == textwrap.dedent(
            """\
            False
            4
                Repeat: (Or: {Word, Newline+}, 4, 4)
                    Or: {Word, Newline+}
                        Word
                            Word <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    Or: {Word, Newline+}
                        Newline+
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
@pytest.mark.asyncio
async def test_ParseReturnsNone(parse_mock):
    # ----------------------------------------------------------------------
    class NoneStatement(Statement):
        # ----------------------------------------------------------------------
        @Interface.override
        def Clone(
            self,
            unique_id: List[str],
        ):
            return self.CloneImpl(
                self.Name,
                unique_id=unique_id,
                type_id=self.TypeId,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def ParseAsync(self, *args, **kwargs):
            return None

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        @Interface.override
        def PopulateRecursiveImpl(
            self,
            new_statement: Statement,
        ) -> bool:
            # Nothing to do here
            return False

    # ----------------------------------------------------------------------

    statement = RepeatStatement(NoneStatement("None Statement"), 1, None)

    result = await statement.ParseAsync(CreateIterator("test"), parse_mock)
    assert result is None

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_OnInternalStatementFalse(parse_mock):
    parse_mock.OnInternalStatementAsync = CoroutineMock(return_value=False)

    statement = RepeatStatement(TokenStatement(NewlineToken()), 1, None)

    result = await statement.ParseAsync(
        CreateIterator(
            textwrap.dedent(
                """\




                """,
            ),
        ),
        parse_mock,
    )

    assert result is None
