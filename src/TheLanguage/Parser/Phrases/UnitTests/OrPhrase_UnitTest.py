# ----------------------------------------------------------------------
# |
# |  OrPhrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-28 07:05:27
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
    from ..OrPhrase import *

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

        result = await self._phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                            IsIgnored  : False
                                            IterBegin_ : [1, 1] (0)
                                            IterEnd    : [1, 10] (9)
                                            Token      : lower
                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                         Match : <_sre.SRE_Match object; span=(0, 9), match='lowercase'>
                                            Whitespace : None
                                 Phrase   : lower
                      Phrase   : My Or Phrase
            Iter    : [1, 10] (9)
            Success : True
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchUpper(self, parse_mock):
        iter = CreateIterator("UPPERCASE")

        result = await self._phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                            IsIgnored  : False
                                            IterBegin_ : [1, 1] (0)
                                            IterEnd    : [1, 10] (9)
                                            Token      : upper
                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                         Match : <_sre.SRE_Match object; span=(0, 9), match='UPPERCASE'>
                                            Whitespace : None
                                 Phrase   : upper
                      Phrase   : My Or Phrase
            Iter    : [1, 10] (9)
            Success : True
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNumber(self, parse_mock):
        iter = CreateIterator("12345678")

        result = await self._phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                            IsIgnored  : False
                                            IterBegin_ : [1, 1] (0)
                                            IterEnd    : [1, 9] (8)
                                            Token      : number
                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                         Match : <_sre.SRE_Match object; span=(0, 8), match='12345678'>
                                            Whitespace : None
                                 Phrase   : number
                      Phrase   : My Or Phrase
            Iter    : [1, 9] (8)
            Success : True
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNumberSingleThreaded(self, parse_mock):
        iter = CreateIterator("12345678")

        result = await self._phrase.ParseAsync(
            ["root"],
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                            IsIgnored  : False
                                            IterBegin_ : [1, 1] (0)
                                            IterEnd    : [1, 9] (8)
                                            Token      : number
                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                         Match : <_sre.SRE_Match object; span=(0, 8), match='12345678'>
                                            Whitespace : None
                                 Phrase   : number
                      Phrase   : My Or Phrase
            Iter    : [1, 9] (8)
            Success : True
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_OnInternalPhraseReturnsNone(self, parse_mock):
        parse_mock.OnInternalPhraseAsync = CoroutineMock(return_value=None)

        iter = CreateIterator("12345678")

        result = await self._phrase.ParseAsync(["root"], iter, parse_mock)
        assert result is None

        assert len(parse_mock.method_calls) == 11

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = await self._phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : lower
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : upper
                                              2)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : number
                                              3)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : Newline+
                                 IsComplete : True
                      Phrase   : My Or Phrase
            Iter    : [1, 1] (0)
            Success : False
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchSingleThreaded(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = await self._phrase.ParseAsync(
            ["root"],
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : lower
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : upper
                                              2)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : number
                                              3)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : Newline+
                                 IsComplete : True
                      Phrase   : My Or Phrase
            Iter    : [1, 1] (0)
            Success : False
            """,
        )

        assert iter.Offset == 0
        assert result.Iter.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedLower(self, parse_mock):
        result = await self._outer_nested_phrase.ParseAsync(
            ["root"],
            CreateIterator("word"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                            Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                       IsIgnored  : False
                                                       IterBegin_ : [1, 1] (0)
                                                       IterEnd    : [1, 5] (4)
                                                       Token      : lower
                                                       Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                    Match : <_sre.SRE_Match object; span=(0, 4), match='word'>
                                                       Whitespace : None
                                            Phrase   : lower
                                 Phrase   : Or: (lower, number)
                      Phrase   : Or: (upper, Or: (lower, number))
            Iter    : [1, 5] (4)
            Success : True
            """,
        )

        assert len(parse_mock.method_calls) == 13

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedLowerEvents(self, parse_mock):
        result = await self._outer_nested_phrase.ParseAsync(
            ["root"],
            CreateIterator("word"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                            Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                       IsIgnored  : False
                                                       IterBegin_ : [1, 1] (0)
                                                       IterEnd    : [1, 5] (4)
                                                       Token      : lower
                                                       Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                    Match : <_sre.SRE_Match object; span=(0, 4), match='word'>
                                                       Whitespace : None
                                            Phrase   : lower
                                 Phrase   : Or: (lower, number)
                      Phrase   : Or: (upper, Or: (lower, number))
            Iter    : [1, 5] (4)
            Success : True
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Or: (upper, Or: (lower, number))"
            1) StartPhrase, "upper", "Or: (upper, Or: (lower, number))"
            2) EndPhrase, "upper" [False], "Or: (upper, Or: (lower, number))" [None]
            3) StartPhrase, "Or: (lower, number)", "Or: (upper, Or: (lower, number))"
            4) StartPhrase, "lower", "Or: (lower, number)", "Or: (upper, Or: (lower, number))"
            5) OnInternalPhraseAsync, 0, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                           IsIgnored  : False
                           IterBegin_ : [1, 1] (0)
                           IterEnd    : [1, 5] (4)
                           Token      : lower
                           Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                        Match : <_sre.SRE_Match object; span=(0, 4), match='word'>
                           Whitespace : None
                Phrase   : lower
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : -- empty list --
                           IsComplete : False
                Phrase   : Or: (lower, number)
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                             Data     : None
                                             Phrase   : upper
                           IsComplete : False
                Phrase   : Or: (upper, Or: (lower, number))
            6) EndPhrase, "lower" [True], "Or: (lower, number)" [None], "Or: (upper, Or: (lower, number))" [None]
            7) StartPhrase, "number", "Or: (lower, number)", "Or: (upper, Or: (lower, number))"
            8) EndPhrase, "number" [False], "Or: (lower, number)" [None], "Or: (upper, Or: (lower, number))" [None]
            9) OnInternalPhraseAsync, 0, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                           Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                      IsIgnored  : False
                                      IterBegin_ : [1, 1] (0)
                                      IterEnd    : [1, 5] (4)
                                      Token      : lower
                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                   Match : <_sre.SRE_Match object; span=(0, 4), match='word'>
                                      Whitespace : None
                           Phrase   : lower
                Phrase   : Or: (lower, number)
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                           DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                             Data     : None
                                             Phrase   : upper
                           IsComplete : False
                Phrase   : Or: (upper, Or: (lower, number))
            10) EndPhrase, "Or: (lower, number)" [True], "Or: (upper, Or: (lower, number))" [None]
            11) OnInternalPhraseAsync, 0, 4
                <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                           Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                                 IsIgnored  : False
                                                 IterBegin_ : [1, 1] (0)
                                                 IterEnd    : [1, 5] (4)
                                                 Token      : lower
                                                 Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                              Match : <_sre.SRE_Match object; span=(0, 4), match='word'>
                                                 Whitespace : None
                                      Phrase   : lower
                           Phrase   : Or: (lower, number)
                Phrase   : Or: (upper, Or: (lower, number))
            12) EndPhrase, "Or: (upper, Or: (lower, number))" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedUpper(self, parse_mock):
        result = await self._outer_nested_phrase.ParseAsync(
            ["root"],
            CreateIterator("WORD"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                            IsIgnored  : False
                                            IterBegin_ : [1, 1] (0)
                                            IterEnd    : [1, 5] (4)
                                            Token      : upper
                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                         Match : <_sre.SRE_Match object; span=(0, 4), match='WORD'>
                                            Whitespace : None
                                 Phrase   : upper
                      Phrase   : Or: (upper, Or: (lower, number))
            Iter    : [1, 5] (4)
            Success : True
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

        result = await self._sort_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                            IsIgnored  : False
                                            IterBegin_ : [1, 1] (0)
                                            IterEnd    : [1, 5] (4)
                                            Token      : Long
                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                         Match : <_sre.SRE_Match object; span=(0, 4), match='1234'>
                                            Whitespace : None
                                 Phrase   : Long
                      Phrase   : Sort
            Iter    : [1, 5] (4)
            Success : True
            """,
        )

        assert len(parse_mock.method_calls) == 9


    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoSort(self, parse_mock):
        iter = CreateIterator("1234")

        result = await self._no_sort_phrase.ParseAsync(["root"], iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                 Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.TokenParseResultData'>
                                            IsIgnored  : False
                                            IterBegin_ : [1, 1] (0)
                                            IterEnd    : [1, 3] (2)
                                            Token      : Short
                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                         Match : <_sre.SRE_Match object; span=(0, 2), match='12'>
                                            Whitespace : None
                                 Phrase   : Short
                      Phrase   : No Sort
            Iter    : [1, 3] (2)
            Success : True
            """,
        )

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchNoSort(self, parse_mock):
        result = await self._no_sort_phrase.ParseAsync(["root"], CreateIterator("!1122"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.Phrase.Phrase.MultipleStandardParseResultData'>
                                 DataItems  : 0)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : Short
                                              1)   <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                                                   Data     : None
                                                   Phrase   : Long
                                 IsComplete : True
                      Phrase   : No Sort
            Iter    : [1, 1] (0)
            Success : False
            """,
        )

        assert result.Iter.AtEnd() == False
        assert len(parse_mock.method_calls) == 6

# ----------------------------------------------------------------------
class TestParseReturnsNone(object):
    # ----------------------------------------------------------------------
    class EmptyPhrase(Phrase):
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
        result = await self._phrase.ParseAsync(["root"], CreateIterator("test"), parse_mock)
        assert result is None

        assert len(parse_mock.method_calls) == 2

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_StandardSingleThreaded(self, parse_mock):
        result = await self._phrase.ParseAsync(
            ["root"],
            CreateIterator("test"),
            parse_mock,
            single_threaded=True,
        )
        assert result is None

        assert len(parse_mock.method_calls) == 2
