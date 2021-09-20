# ----------------------------------------------------------------------
# |
# |  DynamicPhrase_UnitTest.py
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
"""Unit test for DynamicPhrase.py"""

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
    from ..DynamicPhrase import *
    from ..TokenPhrase import TokenPhrase, RegexToken

    from ...Components.UnitTests import (
        CreateIterator,
        MethodCallsToString,
        parse_mock,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _lower_phrase                           = TokenPhrase(RegexToken("lower", re.compile(r"(?P<value>[a-z]+)")))
    _number_phrase                          = TokenPhrase(RegexToken("number", re.compile(r"(?P<value>[0-9]+)")))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Single(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (None, [self._lower_phrase]),
        )

        result = await phrase.LexAsync(("root", ), CreateIterator("word"), parse_mock)
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
                Phrase: "Or: (lower)"
              Phrase: "Dynamic Phrases"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 5] (4)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleNoMatch(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (None, [self._lower_phrase]),
        )

        result = await phrase.LexAsync(("root", ), CreateIterator("1234"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleStandardLexResultData'>
                  DataItems:
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: None
                      Phrase: "lower"
                  IsComplete: True
                Phrase: "Or: (lower)"
              Phrase: "Dynamic Phrases"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: False
            """,
        )

        assert len(parse_mock.method_calls) == 6

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleNumber(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (None, [self._lower_phrase, self._number_phrase]),
        )

        result = await phrase.LexAsync(("root", ), CreateIterator("1234"), parse_mock)
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
                    Token: "number"
                    Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                      Match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                    Whitespace: None
                  Phrase: "number"
                Phrase: "Or: (lower, number)"
              Phrase: "Dynamic Phrases"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 5] (4)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleLower(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (None, [self._lower_phrase, self._number_phrase]),
        )

        result = await phrase.LexAsync(("root", ), CreateIterator("word"), parse_mock)
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
                Phrase: "Or: (lower, number)"
              Phrase: "Dynamic Phrases"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 5] (4)"
            Success: True
            """,
        )

        assert len(parse_mock.method_calls) == 11

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleNumberEvents(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (None, [self._lower_phrase, self._number_phrase]),
        )

        result = await phrase.LexAsync(
            ("root", ),
            CreateIterator("1234"),
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
                    Token: "number"
                    Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                      Match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                    Whitespace: None
                  Phrase: "number"
                Phrase: "Or: (lower, number)"
              Phrase: "Dynamic Phrases"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 5] (4)"
            Success: True
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Dynamic Phrases"
            1) StartPhrase, "Or: (lower, number)", "Dynamic Phrases"
            2) StartPhrase, "number", "Or: (lower, number)", "Dynamic Phrases"
            3) OnInternalPhraseAsync, 0, 4
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  IsIgnored: False
                  IterBegin: "[1, 1] (0)"
                  IterEnd: "[1, 5] (4)"
                  Token: "number"
                  Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                    Match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                  Whitespace: None
                Phrase: "number"
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleStandardLexResultData'>
                  DataItems:
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: None
                      Phrase: "lower"
                  IsComplete: False
                Phrase: "Or: (lower, number)"
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleStandardLexResultData'>
                  DataItems:
                    - None
                  IsComplete: False
                Phrase: "Dynamic Phrases"
            4) EndPhrase, "number" [True], "Or: (lower, number)" [None], "Dynamic Phrases" [None]
            5) OnInternalPhraseAsync, 0, 4
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                  Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    IsIgnored: False
                    IterBegin: "[1, 1] (0)"
                    IterEnd: "[1, 5] (4)"
                    Token: "number"
                    Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                      Match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                    Whitespace: None
                  Phrase: "number"
                Phrase: "Or: (lower, number)"
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleStandardLexResultData'>
                  DataItems:
                    - None
                  IsComplete: False
                Phrase: "Dynamic Phrases"
            6) EndPhrase, "Or: (lower, number)" [True], "Dynamic Phrases" [None]
            7) OnInternalPhraseAsync, 0, 4
                # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                  Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                    Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      IsIgnored: False
                      IterBegin: "[1, 1] (0)"
                      IterEnd: "[1, 5] (4)"
                      Token: "number"
                      Value: # <class 'TheLanguage.Lexer.Components.Token.RegexToken.MatchResult'>
                        Match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                      Whitespace: None
                    Phrase: "number"
                  Phrase: "Or: (lower, number)"
                Phrase: "Dynamic Phrases"
            8) EndPhrase, "Dynamic Phrases" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleNoMatchEvents(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (None, [self._lower_phrase]),
        )

        result = await phrase.LexAsync(
            ("root", ),
            CreateIterator("1234"),
            parse_mock,
            single_threaded=True,
        )
        assert str(result) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                Data: # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.MultipleStandardLexResultData'>
                  DataItems:
                    - # <class 'TheLanguage.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
                      Data: None
                      Phrase: "lower"
                  IsComplete: True
                Phrase: "Or: (lower)"
              Phrase: "Dynamic Phrases"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: False
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Dynamic Phrases"
            1) StartPhrase, "Or: (lower)", "Dynamic Phrases"
            2) EndPhrase, "Or: (lower)" [False], "Dynamic Phrases" [None]
            3) EndPhrase, "Dynamic Phrases" [False]
            """,
        )