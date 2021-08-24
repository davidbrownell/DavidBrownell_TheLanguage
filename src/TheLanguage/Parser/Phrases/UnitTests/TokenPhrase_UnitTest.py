# ----------------------------------------------------------------------
# |
# |  TokenPhrase_UnitTest.py
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
"""Unit test for TokenPhrase.py"""

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
    from ..TokenPhrase import *

    from ...Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )

    from ...Components.UnitTests import (
        CoroutineMock,
        CreateIterator,
        parse_mock,
        MethodCallsToString,
    )


# ----------------------------------------------------------------------
class TestWords(object):
    _word_phrase                            = TokenPhrase(RegexToken("Word", re.compile(r"(?P<value>[a-zA-Z0-9]+)\b")))
    _newline_phrase                         = TokenPhrase(NewlineToken())
    _indent_phrase                          = TokenPhrase(IndentToken())
    _dedent_phrase                          = TokenPhrase(DedentToken())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        iter = CreateIterator("This      is\ta \t\t   test\t  \n")

        # This
        result = await self._word_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 1] (0)
                                 IterEnd    : [1, 5] (4)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(0, 4), match='This'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [1, 1] (0)
            IterE   : [1, 5] (4)
            Success : True
            """,
        )

        assert iter.Offset == 0
        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhraseAsync, 0, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 1] (0)
                           IterEnd    : [1, 5] (4)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(0, 4), match='This'>
                           Whitespace : None
                Phrase   : Word
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # is
        result = await self._word_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 11] (10)
                                 IterEnd    : [1, 13] (12)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(10, 12), match='is'>
                                 Whitespace : 0)   4
                                              1)   10
                      Phrase   : Word
            IterB   : [1, 5] (4)
            IterE   : [1, 13] (12)
            Success : True
            """,
        )

        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhraseAsync, 10, 12
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 11] (10)
                           IterEnd    : [1, 13] (12)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(10, 12), match='is'>
                           Whitespace : 0)   4
                                        1)   10
                Phrase   : Word
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # a
        result = await self._word_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 14] (13)
                                 IterEnd    : [1, 15] (14)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(13, 14), match='a'>
                                 Whitespace : 0)   12
                                              1)   13
                      Phrase   : Word
            IterB   : [1, 13] (12)
            IterE   : [1, 15] (14)
            Success : True
            """,
        )

        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhraseAsync, 13, 14
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 14] (13)
                           IterEnd    : [1, 15] (14)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(13, 14), match='a'>
                           Whitespace : 0)   12
                                        1)   13
                Phrase   : Word
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # test
        result = await self._word_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 21] (20)
                                 IterEnd    : [1, 25] (24)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(20, 24), match='test'>
                                 Whitespace : 0)   14
                                              1)   20
                      Phrase   : Word
            IterB   : [1, 15] (14)
            IterE   : [1, 25] (24)
            Success : True
            """,
        )

        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhraseAsync, 20, 24
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 21] (20)
                           IterEnd    : [1, 25] (24)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(20, 24), match='test'>
                           Whitespace : 0)   14
                                        1)   20
                Phrase   : Word
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # Newline
        result = await self._newline_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 28] (27)
                                 IterEnd    : [2, 1] (28)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 28
                                              Start : 27
                                 Whitespace : 0)   24
                                              1)   27
                      Phrase   : Newline+
            IterB   : [1, 25] (24)
            IterE   : [2, 1] (28)
            Success : True
            """,
        )

        assert result.IterE.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Newline+"
            1) OnInternalPhraseAsync, 27, 28
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 28] (27)
                           IterEnd    : [2, 1] (28)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 28
                                        Start : 27
                           Whitespace : 0)   24
                                        1)   27
                Phrase   : Newline+
            2) EndPhrase, "Newline+" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NotAMatch(self, parse_mock):
        iter = CreateIterator("te__")

        result = await self._word_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : None
                      Phrase   : Word
            IterB   : [1, 1] (0)
            IterE   : [1, 1] (0)
            Success : False
            """,
        )

        assert iter.Offset == 0
        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) EndPhrase, "Word" [False]
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
        result = await self._word_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 1] (0)
                                 IterEnd    : [1, 4] (3)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [1, 1] (0)
            IterE   : [1, 4] (3)
            Success : True
            """,
        )

        assert iter.Offset == 0
        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhraseAsync, 0, 3
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 1] (0)
                           IterEnd    : [1, 4] (3)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                           Whitespace : None
                Phrase   : Word
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # Newline
        result = await self._newline_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 4] (3)
                                 IterEnd    : [2, 1] (4)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 4
                                              Start : 3
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [1, 4] (3)
            IterE   : [2, 1] (4)
            Success : True
            """,
        )

        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Newline+"
            1) OnInternalPhraseAsync, 3, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 4] (3)
                           IterEnd    : [2, 1] (4)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 4
                                        Start : 3
                           Whitespace : None
                Phrase   : Newline+
            2) EndPhrase, "Newline+" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # Indent
        result = await self._indent_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [2, 1] (4)
                                 IterEnd    : [2, 5] (8)
                                 Token      : Indent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                              End   : 8
                                              Start : 4
                                              Value : 4
                                 Whitespace : None
                      Phrase   : Indent
            IterB   : [2, 1] (4)
            IterE   : [2, 5] (8)
            Success : True
            """,
        )

        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Indent"
            1) OnIndentAsync, 4, 8
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [2, 1] (4)
                           IterEnd    : [2, 5] (8)
                           Token      : Indent
                           Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                        End   : 8
                                        Start : 4
                                        Value : 4
                           Whitespace : None
                Phrase   : Indent
            2) EndPhrase, "Indent" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # two
        result = await self._word_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [2, 5] (8)
                                 IterEnd    : [2, 8] (11)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(8, 11), match='two'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [2, 5] (8)
            IterE   : [2, 8] (11)
            Success : True
            """,
        )

        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhraseAsync, 8, 11
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [2, 5] (8)
                           IterEnd    : [2, 8] (11)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(8, 11), match='two'>
                           Whitespace : None
                Phrase   : Word
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # Newline
        result = await self._newline_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [2, 8] (11)
                                 IterEnd    : [3, 1] (12)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 12
                                              Start : 11
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [2, 8] (11)
            IterE   : [3, 1] (12)
            Success : True
            """,
        )

        assert result.IterE.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Newline+"
            1) OnInternalPhraseAsync, 11, 12
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [2, 8] (11)
                           IterEnd    : [3, 1] (12)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 12
                                        Start : 11
                           Whitespace : None
                Phrase   : Newline+
            2) EndPhrase, "Newline+" [True]
            """,
        )

        iter = result.IterE
        parse_mock.reset_mock()

        # Dedent
        result = await self._dedent_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [3, 1] (12)
                                 IterEnd    : [3, 1] (12)
                                 Token      : Dedent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                              -- empty dict --
                                 Whitespace : None
                      Phrase   : Dedent
            IterB   : [3, 1] (12)
            IterE   : [3, 1] (12)
            Success : True
            """,
        )

        assert result.IterE.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Dedent"
            1) OnDedentAsync, 12, 12
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [3, 1] (12)
                           IterEnd    : [3, 1] (12)
                           Token      : Dedent
                           Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                        -- empty dict --
                           Whitespace : None
                Phrase   : Dedent
            2) EndPhrase, "Dedent" [True]
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

        for expected_phrase in [
            # one
            self._word_phrase,
            self._newline_phrase,

            # two
            self._indent_phrase,
            self._word_phrase,
            self._newline_phrase,

            # three
            self._indent_phrase,
            self._word_phrase,
            self._newline_phrase,

            # four
            self._word_phrase,
            self._newline_phrase,

            # five
            self._dedent_phrase,
            self._word_phrase,
            self._newline_phrase,

            # six
            self._indent_phrase,
            self._word_phrase,
            self._newline_phrase,

            # seven
            self._dedent_phrase,
            self._word_phrase,
            self._newline_phrase,

            # eight
            self._indent_phrase,
            self._word_phrase,
            self._newline_phrase,

            # eof
            self._dedent_phrase,
            self._dedent_phrase,
        ]:
            results.append(await expected_phrase.ParseAsync(["root"], iter, parse_mock))
            iter = results[-1].IterE.Clone()

        assert iter.AtEnd()

        assert "\n".join([str(result) for result in results]) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 1] (0)
                                 IterEnd    : [1, 4] (3)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [1, 1] (0)
            IterE   : [1, 4] (3)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [1, 4] (3)
                                 IterEnd    : [2, 1] (4)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 4
                                              Start : 3
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [1, 4] (3)
            IterE   : [2, 1] (4)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [2, 1] (4)
                                 IterEnd    : [2, 5] (8)
                                 Token      : Indent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                              End   : 8
                                              Start : 4
                                              Value : 4
                                 Whitespace : None
                      Phrase   : Indent
            IterB   : [2, 1] (4)
            IterE   : [2, 5] (8)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [2, 5] (8)
                                 IterEnd    : [2, 8] (11)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(8, 11), match='two'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [2, 5] (8)
            IterE   : [2, 8] (11)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [2, 8] (11)
                                 IterEnd    : [3, 1] (12)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 12
                                              Start : 11
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [2, 8] (11)
            IterE   : [3, 1] (12)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [3, 1] (12)
                                 IterEnd    : [3, 9] (20)
                                 Token      : Indent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                              End   : 20
                                              Start : 12
                                              Value : 8
                                 Whitespace : None
                      Phrase   : Indent
            IterB   : [3, 1] (12)
            IterE   : [3, 9] (20)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [3, 9] (20)
                                 IterEnd    : [3, 14] (25)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(20, 25), match='three'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [3, 9] (20)
            IterE   : [3, 14] (25)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [3, 14] (25)
                                 IterEnd    : [4, 1] (26)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 26
                                              Start : 25
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [3, 14] (25)
            IterE   : [4, 1] (26)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [4, 9] (34)
                                 IterEnd    : [4, 13] (38)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(34, 38), match='four'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [4, 1] (26)
            IterE   : [4, 13] (38)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [4, 13] (38)
                                 IterEnd    : [5, 1] (39)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 39
                                              Start : 38
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [4, 13] (38)
            IterE   : [5, 1] (39)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [5, 1] (39)
                                 IterEnd    : [5, 5] (43)
                                 Token      : Dedent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                              -- empty dict --
                                 Whitespace : None
                      Phrase   : Dedent
            IterB   : [5, 1] (39)
            IterE   : [5, 5] (43)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [5, 5] (43)
                                 IterEnd    : [5, 9] (47)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(43, 47), match='five'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [5, 5] (43)
            IterE   : [5, 9] (47)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [5, 9] (47)
                                 IterEnd    : [6, 1] (48)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 48
                                              Start : 47
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [5, 9] (47)
            IterE   : [6, 1] (48)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [6, 1] (48)
                                 IterEnd    : [6, 13] (60)
                                 Token      : Indent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                              End   : 60
                                              Start : 48
                                              Value : 12
                                 Whitespace : None
                      Phrase   : Indent
            IterB   : [6, 1] (48)
            IterE   : [6, 13] (60)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [6, 13] (60)
                                 IterEnd    : [6, 16] (63)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(60, 63), match='six'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [6, 13] (60)
            IterE   : [6, 16] (63)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [6, 16] (63)
                                 IterEnd    : [7, 1] (64)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 64
                                              Start : 63
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [6, 16] (63)
            IterE   : [7, 1] (64)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [7, 1] (64)
                                 IterEnd    : [7, 5] (68)
                                 Token      : Dedent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                              -- empty dict --
                                 Whitespace : None
                      Phrase   : Dedent
            IterB   : [7, 1] (64)
            IterE   : [7, 5] (68)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [7, 5] (68)
                                 IterEnd    : [7, 10] (73)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(68, 73), match='seven'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [7, 5] (68)
            IterE   : [7, 10] (73)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [7, 10] (73)
                                 IterEnd    : [8, 1] (74)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 74
                                              Start : 73
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [7, 10] (73)
            IterE   : [8, 1] (74)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [8, 1] (74)
                                 IterEnd    : [8, 9] (82)
                                 Token      : Indent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                              End   : 82
                                              Start : 74
                                              Value : 8
                                 Whitespace : None
                      Phrase   : Indent
            IterB   : [8, 1] (74)
            IterE   : [8, 9] (82)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [8, 9] (82)
                                 IterEnd    : [8, 14] (87)
                                 Token      : Word
                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                              Match : <_sre.SRE_Match object; span=(82, 87), match='eight'>
                                 Whitespace : None
                      Phrase   : Word
            IterB   : [8, 9] (82)
            IterE   : [8, 14] (87)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [8, 14] (87)
                                 IterEnd    : [9, 1] (88)
                                 Token      : Newline+
                                 Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                              End   : 88
                                              Start : 87
                                 Whitespace : None
                      Phrase   : Newline+
            IterB   : [8, 14] (87)
            IterE   : [9, 1] (88)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [9, 1] (88)
                                 IterEnd    : [9, 1] (88)
                                 Token      : Dedent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                              -- empty dict --
                                 Whitespace : None
                      Phrase   : Dedent
            IterB   : [9, 1] (88)
            IterE   : [9, 1] (88)
            Success : True

            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                 IsIgnored  : False
                                 IterBegin  : [9, 1] (88)
                                 IterEnd    : [9, 1] (88)
                                 Token      : Dedent
                                 Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                              -- empty dict --
                                 Whitespace : None
                      Phrase   : Dedent
            IterB   : [9, 1] (88)
            IterE   : [9, 1] (88)
            Success : True
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhraseAsync, 0, 3
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 1] (0)
                           IterEnd    : [1, 4] (3)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                           Whitespace : None
                Phrase   : Word
            2) EndPhrase, "Word" [True]
            3) StartPhrase, "Newline+"
            4) OnInternalPhraseAsync, 3, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [1, 4] (3)
                           IterEnd    : [2, 1] (4)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 4
                                        Start : 3
                           Whitespace : None
                Phrase   : Newline+
            5) EndPhrase, "Newline+" [True]
            6) StartPhrase, "Indent"
            7) OnIndentAsync, 4, 8
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [2, 1] (4)
                           IterEnd    : [2, 5] (8)
                           Token      : Indent
                           Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                        End   : 8
                                        Start : 4
                                        Value : 4
                           Whitespace : None
                Phrase   : Indent
            8) EndPhrase, "Indent" [True]
            9) StartPhrase, "Word"
            10) OnInternalPhraseAsync, 8, 11
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [2, 5] (8)
                           IterEnd    : [2, 8] (11)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(8, 11), match='two'>
                           Whitespace : None
                Phrase   : Word
            11) EndPhrase, "Word" [True]
            12) StartPhrase, "Newline+"
            13) OnInternalPhraseAsync, 11, 12
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [2, 8] (11)
                           IterEnd    : [3, 1] (12)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 12
                                        Start : 11
                           Whitespace : None
                Phrase   : Newline+
            14) EndPhrase, "Newline+" [True]
            15) StartPhrase, "Indent"
            16) OnIndentAsync, 12, 20
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [3, 1] (12)
                           IterEnd    : [3, 9] (20)
                           Token      : Indent
                           Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                        End   : 20
                                        Start : 12
                                        Value : 8
                           Whitespace : None
                Phrase   : Indent
            17) EndPhrase, "Indent" [True]
            18) StartPhrase, "Word"
            19) OnInternalPhraseAsync, 20, 25
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [3, 9] (20)
                           IterEnd    : [3, 14] (25)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(20, 25), match='three'>
                           Whitespace : None
                Phrase   : Word
            20) EndPhrase, "Word" [True]
            21) StartPhrase, "Newline+"
            22) OnInternalPhraseAsync, 25, 26
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [3, 14] (25)
                           IterEnd    : [4, 1] (26)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 26
                                        Start : 25
                           Whitespace : None
                Phrase   : Newline+
            23) EndPhrase, "Newline+" [True]
            24) StartPhrase, "Word"
            25) OnInternalPhraseAsync, 34, 38
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [4, 9] (34)
                           IterEnd    : [4, 13] (38)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(34, 38), match='four'>
                           Whitespace : None
                Phrase   : Word
            26) EndPhrase, "Word" [True]
            27) StartPhrase, "Newline+"
            28) OnInternalPhraseAsync, 38, 39
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [4, 13] (38)
                           IterEnd    : [5, 1] (39)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 39
                                        Start : 38
                           Whitespace : None
                Phrase   : Newline+
            29) EndPhrase, "Newline+" [True]
            30) StartPhrase, "Dedent"
            31) OnDedentAsync, 39, 43
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [5, 1] (39)
                           IterEnd    : [5, 5] (43)
                           Token      : Dedent
                           Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                        -- empty dict --
                           Whitespace : None
                Phrase   : Dedent
            32) EndPhrase, "Dedent" [True]
            33) StartPhrase, "Word"
            34) OnInternalPhraseAsync, 43, 47
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [5, 5] (43)
                           IterEnd    : [5, 9] (47)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(43, 47), match='five'>
                           Whitespace : None
                Phrase   : Word
            35) EndPhrase, "Word" [True]
            36) StartPhrase, "Newline+"
            37) OnInternalPhraseAsync, 47, 48
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [5, 9] (47)
                           IterEnd    : [6, 1] (48)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 48
                                        Start : 47
                           Whitespace : None
                Phrase   : Newline+
            38) EndPhrase, "Newline+" [True]
            39) StartPhrase, "Indent"
            40) OnIndentAsync, 48, 60
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [6, 1] (48)
                           IterEnd    : [6, 13] (60)
                           Token      : Indent
                           Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                        End   : 60
                                        Start : 48
                                        Value : 12
                           Whitespace : None
                Phrase   : Indent
            41) EndPhrase, "Indent" [True]
            42) StartPhrase, "Word"
            43) OnInternalPhraseAsync, 60, 63
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [6, 13] (60)
                           IterEnd    : [6, 16] (63)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(60, 63), match='six'>
                           Whitespace : None
                Phrase   : Word
            44) EndPhrase, "Word" [True]
            45) StartPhrase, "Newline+"
            46) OnInternalPhraseAsync, 63, 64
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [6, 16] (63)
                           IterEnd    : [7, 1] (64)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 64
                                        Start : 63
                           Whitespace : None
                Phrase   : Newline+
            47) EndPhrase, "Newline+" [True]
            48) StartPhrase, "Dedent"
            49) OnDedentAsync, 64, 68
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [7, 1] (64)
                           IterEnd    : [7, 5] (68)
                           Token      : Dedent
                           Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                        -- empty dict --
                           Whitespace : None
                Phrase   : Dedent
            50) EndPhrase, "Dedent" [True]
            51) StartPhrase, "Word"
            52) OnInternalPhraseAsync, 68, 73
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [7, 5] (68)
                           IterEnd    : [7, 10] (73)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(68, 73), match='seven'>
                           Whitespace : None
                Phrase   : Word
            53) EndPhrase, "Word" [True]
            54) StartPhrase, "Newline+"
            55) OnInternalPhraseAsync, 73, 74
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [7, 10] (73)
                           IterEnd    : [8, 1] (74)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 74
                                        Start : 73
                           Whitespace : None
                Phrase   : Newline+
            56) EndPhrase, "Newline+" [True]
            57) StartPhrase, "Indent"
            58) OnIndentAsync, 74, 82
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [8, 1] (74)
                           IterEnd    : [8, 9] (82)
                           Token      : Indent
                           Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                        End   : 82
                                        Start : 74
                                        Value : 8
                           Whitespace : None
                Phrase   : Indent
            59) EndPhrase, "Indent" [True]
            60) StartPhrase, "Word"
            61) OnInternalPhraseAsync, 82, 87
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [8, 9] (82)
                           IterEnd    : [8, 14] (87)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(82, 87), match='eight'>
                           Whitespace : None
                Phrase   : Word
            62) EndPhrase, "Word" [True]
            63) StartPhrase, "Newline+"
            64) OnInternalPhraseAsync, 87, 88
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [8, 14] (87)
                           IterEnd    : [9, 1] (88)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 88
                                        Start : 87
                           Whitespace : None
                Phrase   : Newline+
            65) EndPhrase, "Newline+" [True]
            66) StartPhrase, "Dedent"
            67) OnDedentAsync, 88, 88
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [9, 1] (88)
                           IterEnd    : [9, 1] (88)
                           Token      : Dedent
                           Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                        -- empty dict --
                           Whitespace : None
                Phrase   : Dedent
            68) EndPhrase, "Dedent" [True]
            69) StartPhrase, "Dedent"
            70) OnDedentAsync, 88, 88
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin  : [9, 1] (88)
                           IterEnd    : [9, 1] (88)
                           Token      : Dedent
                           Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                        -- empty dict --
                           Whitespace : None
                Phrase   : Dedent
            71) EndPhrase, "Dedent" [True]
            """,
        )
