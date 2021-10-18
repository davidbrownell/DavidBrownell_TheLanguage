# ----------------------------------------------------------------------
# |
# |  OrPhrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-24 12:30:11
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for OrPhrase.py"""

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
    from ..DSL import DefaultCommentToken
    from ..OrPhrase import *
    from ..SequencePhrase import SequencePhrase

    from ..TokenPhrase import (
        NewlineToken,
        RegexToken,
        TokenPhrase,
    )

    from ...Components.Token import (
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
class TestStandard(object):
    _lower_phrase                           = TokenPhrase(RegexToken("lower", re.compile(r"(?P<value>[a-z]+[0-9]*)")))
    _upper_phrase                           = TokenPhrase(RegexToken("upper", re.compile(r"(?P<value>[A-Z]+[0-9]*)")))
    _number_phrase                          = TokenPhrase(RegexToken("number", re.compile(r"(?P<value>[0-9]+)")))
    _newline_phrase                         = TokenPhrase(NewlineToken())

    _phrase                                 = OrPhrase(
        [
            _lower_phrase,
            _upper_phrase,
            _number_phrase,
            _newline_phrase,
        ],
        name="My Or Phrase",
    )

    _inner_nested_phrase                    = OrPhrase(
        [
            _lower_phrase,
            _number_phrase,
        ]
    )

    _outer_nested_phrase                    = OrPhrase(
        [
            _upper_phrase,
            _inner_nested_phrase,
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchLower(self, parse_mock):
        iter = CreateIterator("lowercase")

        result = await self._phrase.LexAsync(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 10] (9)"
                  Token: "lower"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 9), match='lowercase'>"
                  Whitespace: None
                Phrase: "lower"
              Phrase: "My Or Phrase"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 10] (9)"
            Success: True
            """,
        )

        assert iter.Offset == 0
        assert result.IterEnd.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchUpper(self, parse_mock):
        iter = CreateIterator("UPPERCASE")

        result = await self._phrase.LexAsync(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 10] (9)"
                  Token: "upper"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 9), match='UPPERCASE'>"
                  Whitespace: None
                Phrase: "upper"
              Phrase: "My Or Phrase"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 10] (9)"
            Success: True
            """,
        )

        assert iter.Offset == 0
        assert result.IterEnd.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNumber(self, parse_mock):
        iter = CreateIterator("12345678")

        result = await self._phrase.LexAsync(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 9] (8)"
                  Token: "number"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 8), match='12345678'>"
                  Whitespace: None
                Phrase: "number"
              Phrase: "My Or Phrase"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 9] (8)"
            Success: True
            """,
        )

        assert iter.Offset == 0
        assert result.IterEnd.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNumberSingleThreaded(self, parse_mock):
        iter = CreateIterator("12345678")

        result = await self._phrase.LexAsync(
            ("root", ),
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 9] (8)"
                  Token: "number"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 8), match='12345678'>"
                  Whitespace: None
                Phrase: "number"
              Phrase: "My Or Phrase"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 9] (8)"
            Success: True
            """,
        )

        assert iter.Offset == 0
        assert result.IterEnd.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_OnInternalPhraseReturnsNone(self, parse_mock):
        parse_mock.OnInternalPhraseAsync = CoroutineMock(return_value=None)

        iter = CreateIterator("12345678")

        result = await self._phrase.LexAsync(
            ("root", ),
            iter,
            parse_mock,
            single_threaded=True,
        )
        assert result is None

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = await self._phrase.LexAsync(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "lower"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "upper"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "number"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "Newline+"
                IsComplete: True
              Phrase: "My Or Phrase"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: False
            """,
        )

        assert iter.Offset == 0
        assert result.IterEnd.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchSingleThreaded(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = await self._phrase.LexAsync(
            ("root", ),
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "lower"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "upper"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "number"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "Newline+"
                IsComplete: True
              Phrase: "My Or Phrase"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: False
            """,
        )

        assert iter.Offset == 0
        assert result.IterEnd.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedLower(self, parse_mock):
        result = await self._outer_nested_phrase.LexAsync(
            ("root", ),
            CreateIterator("word"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                  Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    IsIgnored: False
                    IterBegin: "[1, 1] (0)"
                    IterEnd: "[1, 5] (4)"
                    Token: "lower"
                    Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                      Match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                    Whitespace: None
                  Phrase: "lower"
                Phrase: "(lower | number)"
              Phrase: "(upper | (lower | number))"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 5] (4)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 13

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedLowerEvents(self, parse_mock):
        result = await self._outer_nested_phrase.LexAsync(
            ("root", ),
            CreateIterator("word"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                  Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    IsIgnored: False
                    IterBegin: "[1, 1] (0)"
                    IterEnd: "[1, 5] (4)"
                    Token: "lower"
                    Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                      Match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                    Whitespace: None
                  Phrase: "lower"
                Phrase: "(lower | number)"
              Phrase: "(upper | (lower | number))"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 5] (4)"
            Success: True
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "(upper | (lower | number))"
            1) StartPhrase, "upper"
            2) EndPhrase, "upper" [False]
            3) StartPhrase, "(lower | number)"
            4) StartPhrase, "lower"
            5) OnInternalPhraseAsync, 0, 4
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 5] (4)"
                  Token: "lower"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                  Whitespace: None
                Phrase: "lower"
            6) EndPhrase, "lower" [True]
            7) StartPhrase, "number"
            8) EndPhrase, "number" [False]
            9) OnInternalPhraseAsync, 0, 4
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                  Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    IsIgnored: False
                    IterBegin: "[1, 1] (0)"
                    IterEnd: "[1, 5] (4)"
                    Token: "lower"
                    Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                      Match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                    Whitespace: None
                  Phrase: "lower"
                Phrase: "(lower | number)"
            10) EndPhrase, "(lower | number)" [True]
            11) OnInternalPhraseAsync, 0, 4
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                  Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      IsIgnored: False
                      IterBegin: "[1, 1] (0)"
                      IterEnd: "[1, 5] (4)"
                      Token: "lower"
                      Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                        Match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                      Whitespace: None
                    Phrase: "lower"
                  Phrase: "(lower | number)"
                Phrase: "(upper | (lower | number))"
            12) EndPhrase, "(upper | (lower | number))" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedUpper(self, parse_mock):
        result = await self._outer_nested_phrase.LexAsync(
            ("root", ),
            CreateIterator("WORD"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 5] (4)"
                  Token: "upper"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 4), match='WORD'>"
                  Whitespace: None
                Phrase: "upper"
              Phrase: "(upper | (lower | number))"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 5] (4)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 12

# ----------------------------------------------------------------------
class TestSort(object):
    _short_phrase                           = TokenPhrase(RegexToken("Short", re.compile(r"(?P<value>\d\d)")))
    _long_phrase                            = TokenPhrase(RegexToken("Long", re.compile(r"(?P<value>\d\d\d\d)")))

    _sort_phrase                            = OrPhrase(
        [
            _short_phrase,
            _long_phrase,
        ],
        name="Sort",
        sort_results=True,
    )

    _no_sort_phrase                         = OrPhrase(
        [
            _short_phrase,
            _long_phrase,
        ],
        name="No Sort",
        sort_results=False,
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Sort(self, parse_mock):
        iter = CreateIterator("1234")

        result = await self._sort_phrase.LexAsync(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 5] (4)"
                  Token: "Long"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                  Whitespace: None
                Phrase: "Long"
              Phrase: "Sort"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 5] (4)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 9


    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoSort(self, parse_mock):
        iter = CreateIterator("1234")

        result = await self._no_sort_phrase.LexAsync(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 3] (2)"
                  Token: "Short"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 2), match='12'>"
                  Whitespace: None
                Phrase: "Short"
              Phrase: "No Sort"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 3] (2)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchNoSort(self, parse_mock):
        result = await self._no_sort_phrase.LexAsync(("root", ), CreateIterator("!1122"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "Short"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: None
                    Phrase: "Long"
                IsComplete: True
              Phrase: "No Sort"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: False
            """,
        )

        assert result.IterEnd.AtEnd() == False
        assert len(parse_mock.method_calls) == 6

# ----------------------------------------------------------------------
class TestLexReturnsNone(object):
    # ----------------------------------------------------------------------
    class EmptyPhrase(Phrase):
        # ----------------------------------------------------------------------
        @Interface.override
        async def LexAsync(self, *args, **kwargs):
            return None

        # ----------------------------------------------------------------------
        @Interface.override
        def _PopulateRecursiveImpl(
            self,
            new_phrase: Phrase,
        ) -> bool:
            # Nothing to do here
            return False

    # ----------------------------------------------------------------------

    _phrase                              = OrPhrase(
        # Note that we need 2 phrases so that the implementation doesn't default to a single thread
        [
            EmptyPhrase("1"),
            EmptyPhrase("2"),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Standard(self, parse_mock):
        result = await self._phrase.LexAsync(("root", ), CreateIterator("test"), parse_mock)
        assert result is None

        assert len(parse_mock.method_calls) == 2

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_StandardSingleThreaded(self, parse_mock):
        result = await self._phrase.LexAsync(
            ("root", ),
            CreateIterator("test"),
            parse_mock,
            single_threaded=True,
        )
        assert result is None

        assert len(parse_mock.method_calls) == 2


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_BigFailuresTrumpSmallSuccesses(parse_mock):
    lower_phrase = TokenPhrase(RegexToken("lower", re.compile(r"(?P<value>[a-z]+[0-9]*)")))
    upper_phrase = TokenPhrase(RegexToken("upper", re.compile(r"(?P<value>[A-Z]+[0-9]*)")))

    short_phrase = SequencePhrase(DefaultCommentToken, [lower_phrase])
    long_phrase = SequencePhrase(DefaultCommentToken, [lower_phrase, lower_phrase, upper_phrase])

    or_phrase = OrPhrase([short_phrase, long_phrase])

    iter = CreateIterator("one two three")

    result = await or_phrase.LexAsync(("root", ), iter, parse_mock)
    assert str(result) == textwrap.dedent(
        """\
        # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
        Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
          Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
            DataItems:
              - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                  DataItems:
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "lower"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "lower"
                  IsComplete: True
                Phrase: "[lower]"
              - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                  DataItems:
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "lower"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "lower"
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 5] (4)"
                        IterEnd: "[1, 8] (7)"
                        Token: "lower"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                        Whitespace:
                          - 3
                          - 4
                      Phrase: "lower"
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: None
                      Phrase: "upper"
                  IsComplete: True
                Phrase: "[lower, lower, upper]"
            IsComplete: True
          Phrase: "([lower] | [lower, lower, upper])"
        IterBegin: "[1, 1] (0)"
        IterEnd: "[1, 8] (7)"
        Success: False
        """,
    )
