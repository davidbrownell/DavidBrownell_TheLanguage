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

    from ...Components.Tokens import (
        NewlineToken,
        RegexToken,
    )

    from ...Components.UnitTests import (
        CreateIterator,
        Mock,
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

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 10] (9)"
                  token: "lower"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 9), match='lowercase'>"
                phrase: "lower"
              phrase: "My Or Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 10] (9)"
            success: true
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchUpper(self, parse_mock):
        iter = CreateIterator("UPPERCASE")

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 10] (9)"
                  token: "upper"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 9), match='UPPERCASE'>"
                phrase: "upper"
              phrase: "My Or Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 10] (9)"
            success: true
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNumber(self, parse_mock):
        iter = CreateIterator("12345678")

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 9] (8)"
                  token: "number"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 8), match='12345678'>"
                phrase: "number"
              phrase: "My Or Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 9] (8)"
            success: true
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNumberSingleThreaded(self, parse_mock):
        iter = CreateIterator("12345678")

        result = self._phrase.Lex(
            ("root", ),
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 9] (8)"
                  token: "number"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 8), match='12345678'>"
                phrase: "number"
              phrase: "My Or Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 9] (8)"
            success: true
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_OnInternalPhraseReturnsNone(self, parse_mock):
        parse_mock.OnInternalPhrase = Mock(return_value=None)

        iter = CreateIterator("12345678")

        result = self._phrase.Lex(
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

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "lower"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "upper"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "number"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "Newline+"
              phrase: "My Or Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 1] (0)"
            success: false
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchSingleThreaded(self, parse_mock):
        iter = CreateIterator("!1122334")

        result = self._phrase.Lex(
            ("root", ),
            iter,
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "lower"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "upper"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "number"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "Newline+"
              phrase: "My Or Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 1] (0)"
            success: false
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert len(parse_mock.method_calls) == 10

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedLower(self, parse_mock):
        result = self._outer_nested_phrase.Lex(
            ("root", ),
            CreateIterator("word"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    is_ignored: false
                    iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                      begin: "[1, 1] (0)"
                      end: "[1, 5] (4)"
                    token: "lower"
                    value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                      match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                  phrase: "lower"
                phrase: "(lower | number)"
              phrase: "(upper | (lower | number))"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: true
            """,
        )

        assert len(parse_mock.method_calls) == 13

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedLowerEvents(self, parse_mock):
        result = self._outer_nested_phrase.Lex(
            ("root", ),
            CreateIterator("word"),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    is_ignored: false
                    iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                      begin: "[1, 1] (0)"
                      end: "[1, 5] (4)"
                    token: "lower"
                    value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                      match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                  phrase: "lower"
                phrase: "(lower | number)"
              phrase: "(upper | (lower | number))"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: true
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "(upper | (lower | number))"
            1) StartPhrase, "upper"
            2) EndPhrase, "upper" [False]
            3) StartPhrase, "(lower | number)"
            4) StartPhrase, "lower"
            5) OnInternalPhrase, 0, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 5] (4)"
                  token: "lower"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                phrase: "lower"
            6) EndPhrase, "lower" [True]
            7) StartPhrase, "number"
            8) EndPhrase, "number" [False]
            9) OnInternalPhrase, 0, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    is_ignored: false
                    iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                      begin: "[1, 1] (0)"
                      end: "[1, 5] (4)"
                    token: "lower"
                    value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                      match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                  phrase: "lower"
                phrase: "(lower | number)"
            10) EndPhrase, "(lower | number)" [True]
            11) OnInternalPhrase, 0, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 5] (4)"
                      token: "lower"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 4), match='word'>"
                    phrase: "lower"
                  phrase: "(lower | number)"
                phrase: "(upper | (lower | number))"
            12) EndPhrase, "(upper | (lower | number))" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NestedUpper(self, parse_mock):
        result = self._outer_nested_phrase.Lex(
            ("root", ),
            CreateIterator("WORD"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 5] (4)"
                  token: "upper"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 4), match='WORD'>"
                phrase: "upper"
              phrase: "(upper | (lower | number))"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: true
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

        result = self._sort_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 5] (4)"
                  token: "Long"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                phrase: "Long"
              phrase: "Sort"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: true
            """,
        )

        assert len(parse_mock.method_calls) == 9


    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoSort(self, parse_mock):
        iter = CreateIterator("1234")

        result = self._no_sort_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 3] (2)"
                  token: "Short"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 2), match='12'>"
                phrase: "Short"
              phrase: "No Sort"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 3] (2)"
            success: true
            """,
        )

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchNoSort(self, parse_mock):
        result = self._no_sort_phrase.Lex(("root", ), CreateIterator("!1122"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "Short"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: null
                  phrase: "Long"
              phrase: "No Sort"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 1] (0)"
            success: false
            """,
        )

        assert result.iter_range.end.AtEnd() == False
        assert len(parse_mock.method_calls) == 6

# ----------------------------------------------------------------------
class TestLexReturnsNone(object):
    # ----------------------------------------------------------------------
    class EmptyPhrase(Phrase):
        # ----------------------------------------------------------------------
        @Interface.override
        def Lex(self, *args, **kwargs):
            return None

        # ----------------------------------------------------------------------
        @Interface.override
        def PrettyPrint(self, *args, **kwargs):
            pass

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
        result = self._phrase.Lex(("root", ), CreateIterator("test"), parse_mock)
        assert result is None

        assert len(parse_mock.method_calls) == 2

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_StandardSingleThreaded(self, parse_mock):
        result = self._phrase.Lex(
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

    result = or_phrase.Lex(("root", ), iter, parse_mock)
    assert str(result) == textwrap.dedent(
        """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data:
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        is_ignored: false
                        iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                          begin: "[1, 1] (0)"
                          end: "[1, 4] (3)"
                        token: "lower"
                        value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                          match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                      phrase: "lower"
                  phrase: "[lower]"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data:
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        is_ignored: false
                        iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                          begin: "[1, 1] (0)"
                          end: "[1, 4] (3)"
                        token: "lower"
                        value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                          match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                      phrase: "lower"
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: true
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[1, 5] (4)"
                      token: "HorizontalWhitespace"
                      value: # <class 'v1.Lexer.Components.Tokens.HorizontalWhitespaceToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        is_ignored: false
                        iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                          begin: "[1, 5] (4)"
                          end: "[1, 8] (7)"
                        token: "lower"
                        value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                          match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                      phrase: "lower"
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: null
                      phrase: "upper"
                  phrase: "[lower, lower, upper]"
              phrase: "([lower] | [lower, lower, upper])"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 8] (7)"
            success: false
        """,
    )
