# ----------------------------------------------------------------------
# |
# |  RepeatPhrase_UnitTest.py
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
        result = await self._phrase.ParseAsync(
            ["root"],
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
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [1, 4] (3)
                                                                         IterBefore : [1, 1] (0)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 1] (4)
                                                                         IterBefore : [1, 4] (3)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 4
                                                                                      Start : 3
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                 IsComplete : True
                      Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            Iter    : [2, 1] (4)
            Success : True
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Repeat: {Or: (Word, Newline+), 2, 4}"
            1) StartPhrase, "Or: (Word, Newline+)", "Repeat: {Or: (Word, Newline+), 2, 4}"
            2) StartPhrase, "Word", "Or: (Word, Newline+)", "Repeat: {Or: (Word, Newline+), 2, 4}"
            3) OnInternalPhraseAsync, 0, 3
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterAfter  : [1, 4] (3)
                           IterBefore : [1, 1] (0)
                           Token      : Word
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                           Whitespace : None
                Phrase   : Word
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : -- empty list --
                           IsComplete : False
                Phrase   : Or: (Word, Newline+)
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : -- empty list --
                           IsComplete : False
                Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            4) EndPhrase, "Word" [True], "Or: (Word, Newline+)" [None], "Repeat: {Or: (Word, Newline+), 2, 4}" [None]
            5) StartPhrase, "Newline+", "Or: (Word, Newline+)", "Repeat: {Or: (Word, Newline+), 2, 4}"
            6) EndPhrase, "Newline+" [False], "Or: (Word, Newline+)" [None], "Repeat: {Or: (Word, Newline+), 2, 4}" [None]
            7) OnInternalPhraseAsync, 0, 3
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                           Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                      IsIgnored  : False
                                      IterAfter  : [1, 4] (3)
                                      IterBefore : [1, 1] (0)
                                      Token      : Word
                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                      Whitespace : None
                           Phrase   : Word
                Phrase   : Or: (Word, Newline+)
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : -- empty list --
                           IsComplete : False
                Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            8) EndPhrase, "Or: (Word, Newline+)" [True], "Repeat: {Or: (Word, Newline+), 2, 4}" [None]
            9) StartPhrase, "Or: (Word, Newline+)", "Repeat: {Or: (Word, Newline+), 2, 4}"
            10) StartPhrase, "Word", "Or: (Word, Newline+)", "Repeat: {Or: (Word, Newline+), 2, 4}"
            11) EndPhrase, "Word" [False], "Or: (Word, Newline+)" [None], "Repeat: {Or: (Word, Newline+), 2, 4}" [None]
            12) StartPhrase, "Newline+", "Or: (Word, Newline+)", "Repeat: {Or: (Word, Newline+), 2, 4}"
            13) OnInternalPhraseAsync, 3, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterAfter  : [2, 1] (4)
                           IterBefore : [1, 4] (3)
                           Token      : Newline+
                           Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                        End   : 4
                                        Start : 3
                           Whitespace : None
                Phrase   : Newline+
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                             Data     : None
                                             Phrase   : Word
                           IsComplete : False
                Phrase   : Or: (Word, Newline+)
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                             Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                        IsIgnored  : False
                                                        IterAfter  : [1, 4] (3)
                                                        IterBefore : [1, 1] (0)
                                                        Token      : Word
                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                     Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                        Whitespace : None
                                             Phrase   : Word
                           IsComplete : False
                Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            14) EndPhrase, "Newline+" [True], "Or: (Word, Newline+)" [None], "Repeat: {Or: (Word, Newline+), 2, 4}" [None]
            15) OnInternalPhraseAsync, 3, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                           Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                      IsIgnored  : False
                                      IterAfter  : [2, 1] (4)
                                      IterBefore : [1, 4] (3)
                                      Token      : Newline+
                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                   End   : 4
                                                   Start : 3
                                      Whitespace : None
                           Phrase   : Newline+
                Phrase   : Or: (Word, Newline+)
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                             Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                        IsIgnored  : False
                                                        IterAfter  : [1, 4] (3)
                                                        IterBefore : [1, 1] (0)
                                                        Token      : Word
                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                     Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                        Whitespace : None
                                             Phrase   : Word
                           IsComplete : False
                Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            16) EndPhrase, "Or: (Word, Newline+)" [True], "Repeat: {Or: (Word, Newline+), 2, 4}" [None]
            17) OnInternalPhraseAsync, 0, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                             Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                        Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                   IsIgnored  : False
                                                                   IterAfter  : [1, 4] (3)
                                                                   IterBefore : [1, 1] (0)
                                                                   Token      : Word
                                                                   Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                   Whitespace : None
                                                        Phrase   : Word
                                             Phrase   : Or: (Word, Newline+)
                                        1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                             Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                        Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                   IsIgnored  : False
                                                                   IterAfter  : [2, 1] (4)
                                                                   IterBefore : [1, 4] (3)
                                                                   Token      : Newline+
                                                                   Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                End   : 4
                                                                                Start : 3
                                                                   Whitespace : None
                                                        Phrase   : Newline+
                                             Phrase   : Or: (Word, Newline+)
                           IsComplete : True
                Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            18) EndPhrase, "Repeat: {Or: (Word, Newline+), 2, 4}" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchTwoLines(self, parse_mock):
        result = await self._phrase.ParseAsync(
            ["root"],
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
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [1, 4] (3)
                                                                         IterBefore : [1, 1] (0)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 1] (4)
                                                                         IterBefore : [1, 4] (3)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 4
                                                                                      Start : 3
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                              2)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 4] (7)
                                                                         IterBefore : [2, 1] (4)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              3)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [3, 1] (8)
                                                                         IterBefore : [2, 4] (7)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 8
                                                                                      Start : 7
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                 IsComplete : True
                      Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            Iter    : [3, 1] (8)
            Success : True
            """,
        )

        assert len(parse_mock.method_calls) == 35

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchThreeLines(self, parse_mock):
        result = await self._phrase.ParseAsync(
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
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [1, 4] (3)
                                                                         IterBefore : [1, 1] (0)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 1] (4)
                                                                         IterBefore : [1, 4] (3)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 4
                                                                                      Start : 3
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                              2)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 4] (7)
                                                                         IterBefore : [2, 1] (4)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              3)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [3, 1] (8)
                                                                         IterBefore : [2, 4] (7)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 8
                                                                                      Start : 7
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                 IsComplete : True
                      Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            Iter    : [3, 1] (8)
            Success : True
            """,
        )

        assert len(parse_mock.method_calls) == 35

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        result = await self._phrase.ParseAsync(
            ["root"],
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
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                                              DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                                                Data     : None
                                                                                Phrase   : Word
                                                                           1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                                                Data     : None
                                                                                Phrase   : Newline+
                                                              IsComplete : True
                                                   Phrase   : Or: (Word, Newline+)
                                 IsComplete : True
                      Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            Iter    : [1, 1] (0)
            Success : False
            """,
        )

        assert len(parse_mock.method_calls) == 8

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_partialMatch(self, parse_mock):
        result = await self._phrase.ParseAsync(
            ["root"],
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
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [1, 4] (3)
                                                                         IterBefore : [1, 1] (0)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(0, 3), match='abc'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                                              DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                                                Data     : None
                                                                                Phrase   : Word
                                                                           1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                                                Data     : None
                                                                                Phrase   : Newline+
                                                              IsComplete : True
                                                   Phrase   : Or: (Word, Newline+)
                                 IsComplete : True
                      Phrase   : Repeat: {Or: (Word, Newline+), 2, 4}
            Iter    : [1, 4] (3)
            Success : False
            """,
        )

        assert len(parse_mock.method_calls) == 16

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactMatch(self, parse_mock):
        result = await self._exact_phrase.ParseAsync(
            ["root"],
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
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [1, 4] (3)
                                                                         IterBefore : [1, 1] (0)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 1] (4)
                                                                         IterBefore : [1, 4] (3)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 4
                                                                                      Start : 3
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                              2)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 4] (7)
                                                                         IterBefore : [2, 1] (4)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              3)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [3, 1] (8)
                                                                         IterBefore : [2, 4] (7)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 8
                                                                                      Start : 7
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                 IsComplete : True
                      Phrase   : Repeat: {Or: (Word, Newline+), 4, 4}
            Iter    : [3, 1] (8)
            Success : True
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactLimitedMatch(self, parse_mock):
        result = await self._exact_phrase.ParseAsync(
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
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [1, 4] (3)
                                                                         IterBefore : [1, 1] (0)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 1] (4)
                                                                         IterBefore : [1, 4] (3)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 4
                                                                                      Start : 3
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                              2)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 4] (7)
                                                                         IterBefore : [2, 1] (4)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              3)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [3, 1] (8)
                                                                         IterBefore : [2, 4] (7)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 8
                                                                                      Start : 7
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                 IsComplete : True
                      Phrase   : Repeat: {Or: (Word, Newline+), 4, 4}
            Iter    : [3, 1] (8)
            Success : True
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ExactNoMatch(self, parse_mock):
        result = await self._exact_phrase.ParseAsync(
            ["root"],
            CreateIterator("one"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [1, 4] (3)
                                                                         IterBefore : [1, 1] (0)
                                                                         Token      : Word
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                      Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                         Whitespace : None
                                                              Phrase   : Word
                                                   Phrase   : Or: (Word, Newline+)
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                              Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                                         IsIgnored  : False
                                                                         IterAfter  : [2, 1] (4)
                                                                         IterBefore : [1, 4] (3)
                                                                         Token      : Newline+
                                                                         Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                      End   : 4
                                                                                      Start : 3
                                                                         Whitespace : None
                                                              Phrase   : Newline+
                                                   Phrase   : Or: (Word, Newline+)
                                 IsComplete : True
                      Phrase   : Repeat: {Or: (Word, Newline+), 4, 4}
            Iter    : [2, 1] (4)
            Success : False
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
        async def ParseAsync(self, *args, **kwargs):
            return None

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
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

    result = await phrase.ParseAsync(["root"], CreateIterator("test"), parse_mock)
    assert result is None

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_OnInternalPhraseFalse(parse_mock):
    parse_mock.OnInternalPhraseAsync = CoroutineMock(return_value=False)

    Phrase = RepeatPhrase(TokenPhrase(NewlineToken()), 1, None)

    result = await Phrase.ParseAsync(
        ["root"],
        CreateIterator(
            textwrap.dedent(
                """\




                """,
            ),
        ),
        parse_mock,
    )

    assert result is None