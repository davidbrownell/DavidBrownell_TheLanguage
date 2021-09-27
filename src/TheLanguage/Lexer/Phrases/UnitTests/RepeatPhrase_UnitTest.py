# ----------------------------------------------------------------------
# |
# |  RepeatPhrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-24 14:30:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for RepeatPhrase.py"""

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
    from ..OrPhrase import OrPhrase
    from ..RepeatPhrase import *
    from ..TokenPhrase import (
        NewlineToken,
        RegexToken,
        TokenPhrase,
    )

    from ...Components.Phrase import Phrase
    from ...Components.UnitTests import (
        CoroutineMock,
        CreateIterator,
        MethodCallsToString,
        parse_mock,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _word_phrase                         = TokenPhrase(RegexToken("Word", re.compile(r"(?P<value>[a-zA-Z]+)")))
    _newline_phrase                      = TokenPhrase(NewlineToken())

    _or_phrase                           = OrPhrase([_word_phrase, _newline_phrase])
    _phrase                              = RepeatPhrase(_or_phrase, 2, 4)
    _exact_phrase                        = RepeatPhrase(_or_phrase, 4, 4)

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchSingleLine(self, parse_mock):
        result = await self._phrase.LexAsync(
            ("root", ),
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
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Phrases.RepeatPhrase.RepeatPhrase.RepeatStandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 4] (3)"
                        IterEnd: "[2, 1] (4)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 4
                          Start: 3
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              IgnoredErrorData: None
              Phrase: "{(Word | Newline+), 2, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[2, 1] (4)"
            Success: True
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "{(Word | Newline+), 2, 4}"
            1) StartPhrase, "(Word | Newline+)"
            2) StartPhrase, "Word"
            3) OnInternalPhraseAsync, 0, 3
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 4] (3)"
                  Token: "Word"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                  Whitespace: None
                Phrase: "Word"
            4) EndPhrase, "Word" [True]
            5) StartPhrase, "Newline+"
            6) EndPhrase, "Newline+" [False]
            7) OnInternalPhraseAsync, 0, 3
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                  Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    IsIgnored: False
                    IterBegin: "[1, 1] (0)"
                    IterEnd: "[1, 4] (3)"
                    Token: "Word"
                    Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                      Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    Whitespace: None
                  Phrase: "Word"
                Phrase: "(Word | Newline+)"
            8) EndPhrase, "(Word | Newline+)" [True]
            9) StartPhrase, "(Word | Newline+)"
            10) StartPhrase, "Word"
            11) EndPhrase, "Word" [False]
            12) StartPhrase, "Newline+"
            13) OnInternalPhraseAsync, 3, 4
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 4] (3)"
                  IterEnd: "[2, 1] (4)"
                  Token: "Newline+"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                    End: 4
                    Start: 3
                  Whitespace: None
                Phrase: "Newline+"
            14) EndPhrase, "Newline+" [True]
            15) OnInternalPhraseAsync, 3, 4
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                  Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    IsIgnored: False
                    IterBegin: "[1, 4] (3)"
                    IterEnd: "[2, 1] (4)"
                    Token: "Newline+"
                    Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                      End: 4
                      Start: 3
                    Whitespace: None
                  Phrase: "Newline+"
                Phrase: "(Word | Newline+)"
            16) EndPhrase, "(Word | Newline+)" [True]
            17) OnInternalPhraseAsync, 0, 4
                # <class 'TheLanguage.Lexer.Phrases.RepeatPhrase.RepeatPhrase.RepeatStandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                  DataItems:
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                        Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                          IsIgnored: False
                          IterBegin: "[1, 1] (0)"
                          IterEnd: "[1, 4] (3)"
                          Token: "Word"
                          Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                            Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                          Whitespace: None
                        Phrase: "Word"
                      Phrase: "(Word | Newline+)"
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                        Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                          IsIgnored: False
                          IterBegin: "[1, 4] (3)"
                          IterEnd: "[2, 1] (4)"
                          Token: "Newline+"
                          Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                            End: 4
                            Start: 3
                          Whitespace: None
                        Phrase: "Newline+"
                      Phrase: "(Word | Newline+)"
                  IsComplete: True
                IgnoredErrorData: None
                Phrase: "{(Word | Newline+), 2, 4}"
            18) EndPhrase, "{(Word | Newline+), 2, 4}" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchTwoLines(self, parse_mock):
        result = await self._phrase.LexAsync(
            ("root", ),
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
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Phrases.RepeatPhrase.RepeatPhrase.RepeatStandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 4] (3)"
                        IterEnd: "[2, 1] (4)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 4
                          Start: 3
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 1] (4)"
                        IterEnd: "[2, 4] (7)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 4] (7)"
                        IterEnd: "[3, 1] (8)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 8
                          Start: 7
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              IgnoredErrorData: None
              Phrase: "{(Word | Newline+), 2, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[3, 1] (8)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 35

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchThreeLines(self, parse_mock):
        result = await self._phrase.LexAsync(
            ("root", ),
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
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Phrases.RepeatPhrase.RepeatPhrase.RepeatStandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 4] (3)"
                        IterEnd: "[2, 1] (4)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 4
                          Start: 3
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 1] (4)"
                        IterEnd: "[2, 4] (7)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 4] (7)"
                        IterEnd: "[3, 1] (8)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 8
                          Start: 7
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              IgnoredErrorData: None
              Phrase: "{(Word | Newline+), 2, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[3, 1] (8)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 35

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        result = await self._phrase.LexAsync(
            ("root", ),
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
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                      DataItems:
                        - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                          Data: None
                          Phrase: "Word"
                        - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                          Data: None
                          Phrase: "Newline+"
                      IsComplete: True
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              Phrase: "{(Word | Newline+), 2, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: False
            """,
        )

        assert len(parse_mock.method_calls) == 8

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_partialMatch(self, parse_mock):
        result = await self._phrase.LexAsync(
            ("root", ),
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
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='abc'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                      DataItems:
                        - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                          Data: None
                          Phrase: "Word"
                        - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                          Data: None
                          Phrase: "Newline+"
                      IsComplete: True
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              Phrase: "{(Word | Newline+), 2, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 4] (3)"
            Success: False
            """,
        )

        assert len(parse_mock.method_calls) == 16

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactMatch(self, parse_mock):
        result = await self._exact_phrase.LexAsync(
            ("root", ),
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
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Phrases.RepeatPhrase.RepeatPhrase.RepeatStandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 4] (3)"
                        IterEnd: "[2, 1] (4)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 4
                          Start: 3
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 1] (4)"
                        IterEnd: "[2, 4] (7)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 4] (7)"
                        IterEnd: "[3, 1] (8)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 8
                          Start: 7
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              IgnoredErrorData: None
              Phrase: "{(Word | Newline+), 4, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[3, 1] (8)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactLimitedMatch(self, parse_mock):
        result = await self._exact_phrase.LexAsync(
            ("root", ),
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
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Phrases.RepeatPhrase.RepeatPhrase.RepeatStandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 4] (3)"
                        IterEnd: "[2, 1] (4)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 4
                          Start: 3
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 1] (4)"
                        IterEnd: "[2, 4] (7)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 4] (7)"
                        IterEnd: "[3, 1] (8)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 8
                          Start: 7
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              IgnoredErrorData: None
              Phrase: "{(Word | Newline+), 4, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[3, 1] (8)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactNoMatch(self, parse_mock):
        result = await self._exact_phrase.LexAsync(
            ("root", ),
            CreateIterator("one"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 4] (3)"
                        IterEnd: "[2, 1] (4)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 4
                          Start: 3
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              Phrase: "{(Word | Newline+), 4, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[2, 1] (4)"
            Success: False
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Error2ndLine3rdToken(self, parse_mock):
        result = await self._phrase.LexAsync(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    _expected_match_but_has_underscores
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Phrases.RepeatPhrase.RepeatPhrase.RepeatStandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 4] (3)"
                        IterEnd: "[2, 1] (4)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 4
                          Start: 3
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              IgnoredErrorData: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                  DataItems:
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: None
                      Phrase: "Word"
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: None
                      Phrase: "Newline+"
                  IsComplete: True
                Phrase: "(Word | Newline+)"
              Phrase: "{(Word | Newline+), 2, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[2, 1] (4)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Error2ndLine4thToken(self, parse_mock):
        result = await self._phrase.LexAsync(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    one
                    two _invalid_
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Phrases.RepeatPhrase.RepeatPhrase.RepeatStandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                DataItems:
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 1] (0)"
                        IterEnd: "[1, 4] (3)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[1, 4] (3)"
                        IterEnd: "[2, 1] (4)"
                        Token: "Newline+"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.NewlineToken.MatchResult'>
                          End: 4
                          Start: 3
                        Whitespace: None
                      Phrase: "Newline+"
                    Phrase: "(Word | Newline+)"
                  - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        IsIgnored: False
                        IterBegin: "[2, 1] (4)"
                        IterEnd: "[2, 4] (7)"
                        Token: "Word"
                        Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                          Match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                        Whitespace: None
                      Phrase: "Word"
                    Phrase: "(Word | Newline+)"
                IsComplete: True
              IgnoredErrorData: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleLexResultData'>
                  DataItems:
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: None
                      Phrase: "Word"
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: None
                      Phrase: "Newline+"
                  IsComplete: True
                Phrase: "(Word | Newline+)"
              Phrase: "{(Word | Newline+), 2, 4}"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[2, 4] (7)"
            Success: True
            """,
        )


# ----------------------------------------------------------------------
def test_CreationErrors():
    with pytest.raises(AssertionError):
        RepeatPhrase(TokenPhrase(NewlineToken()), -1, 10)

    with pytest.raises(AssertionError):
        RepeatPhrase(TokenPhrase(NewlineToken()), 10, 5)

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_parseReturnsNone(parse_mock):
    # ----------------------------------------------------------------------
    class NonePhrase(Phrase):
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

    phrase = RepeatPhrase(NonePhrase("None Phrase"), 1, None)

    result = await phrase.LexAsync(("root", ), CreateIterator("test"), parse_mock)
    assert result is None

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_OnInternalPhraseFalse(parse_mock):
    parse_mock.OnInternalPhraseAsync = CoroutineMock(return_value=False)

    Phrase = RepeatPhrase(TokenPhrase(NewlineToken()), 1, None)

    result = await Phrase.LexAsync(
        ("root", ),
        CreateIterator(
            textwrap.dedent(
                """\




                """,
            ),
        ),
        parse_mock,
    )

    assert result is None
