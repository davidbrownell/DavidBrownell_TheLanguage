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
    def test_MatchSingleLine(self, parse_mock):
        result = self._phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[2, 1] (4)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 2, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[2, 1] (4)"
            success: true
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "{(Word | Newline+), 2, 4}"
            1) StartPhrase, "(Word | Newline+)"
            2) StartPhrase, "Word"
            3) OnInternalPhrase, 0, 3
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 4] (3)"
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                phrase: "Word"
            4) EndPhrase, "Word" [True]
            5) StartPhrase, "Newline+"
            6) EndPhrase, "Newline+" [False]
            7) OnInternalPhrase, 0, 3
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    is_ignored: false
                    iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                      begin: "[1, 1] (0)"
                      end: "[1, 4] (3)"
                    token: "Word"
                    value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                      match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                  phrase: "Word"
                phrase: "(Word | Newline+)"
            8) EndPhrase, "(Word | Newline+)" [True]
            9) StartPhrase, "(Word | Newline+)"
            10) StartPhrase, "Word"
            11) EndPhrase, "Word" [False]
            12) StartPhrase, "Newline+"
            13) OnInternalPhrase, 3, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 4] (3)"
                    end: "[2, 1] (4)"
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 3
                      end: 4
                phrase: "Newline+"
            14) EndPhrase, "Newline+" [True]
            15) OnInternalPhrase, 3, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    is_ignored: false
                    iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                      begin: "[1, 4] (3)"
                      end: "[2, 1] (4)"
                    token: "Newline+"
                    value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                      range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                        begin: 3
                        end: 4
                  phrase: "Newline+"
                phrase: "(Word | Newline+)"
            16) EndPhrase, "(Word | Newline+)" [True]
            17) OnInternalPhrase, 0, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data:
                  - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        is_ignored: false
                        iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                          begin: "[1, 1] (0)"
                          end: "[1, 4] (3)"
                        token: "Word"
                        value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                          match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                      phrase: "Word"
                    phrase: "(Word | Newline+)"
                  - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                        is_ignored: false
                        iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                          begin: "[1, 4] (3)"
                          end: "[2, 1] (4)"
                        token: "Newline+"
                        value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                          range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                            begin: 3
                            end: 4
                      phrase: "Newline+"
                    phrase: "(Word | Newline+)"
                phrase: "{(Word | Newline+), 2, 4}"
            18) EndPhrase, "{(Word | Newline+), 2, 4}" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_MatchTwoLines(self, parse_mock):
        result = self._phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[2, 1] (4)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 1] (4)"
                        end: "[2, 4] (7)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 4] (7)"
                        end: "[3, 1] (8)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 7
                          end: 8
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 2, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[3, 1] (8)"
            success: true
            """,
        )

        assert len(parse_mock.method_calls) == 35

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_MatchThreeLines(self, parse_mock):
        result = self._phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[2, 1] (4)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 1] (4)"
                        end: "[2, 4] (7)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 4] (7)"
                        end: "[3, 1] (8)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 7
                          end: 8
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 2, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[3, 1] (8)"
            success: true
            """,
        )

        assert len(parse_mock.method_calls) == 35

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_NoMatch(self, parse_mock):
        result = self._phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data:
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: null
                      phrase: "Word"
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: null
                      phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 2, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 1] (0)"
            success: false
            """,
        )

        assert len(parse_mock.method_calls) == 8

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_partialMatch(self, parse_mock):
        result = self._phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='abc'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data:
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: null
                      phrase: "Word"
                    - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                      data: null
                      phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 2, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 4] (3)"
            success: false
            """,
        )

        assert len(parse_mock.method_calls) == 16

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_ExactMatch(self, parse_mock):
        result = self._exact_phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[2, 1] (4)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 1] (4)"
                        end: "[2, 4] (7)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 4] (7)"
                        end: "[3, 1] (8)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 7
                          end: 8
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 4, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[3, 1] (8)"
            success: true
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_ExactLimitedMatch(self, parse_mock):
        result = self._exact_phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[2, 1] (4)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 1] (4)"
                        end: "[2, 4] (7)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 4] (7)"
                        end: "[3, 1] (8)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 7
                          end: 8
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 4, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[3, 1] (8)"
            success: true
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_ExactNoMatch(self, parse_mock):
        result = self._exact_phrase.Lex(
            ("root", ),
            CreateIterator("one"),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[2, 1] (4)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 4, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[2, 1] (4)"
            success: false
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_Error2ndLine3rdToken(self, parse_mock):
        result = self._phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[2, 1] (4)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 2, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[2, 1] (4)"
            success: true
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_Error2ndLine4thToken(self, parse_mock):
        result = self._phrase.Lex(
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
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 4] (3)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 4] (3)"
                        end: "[2, 1] (4)"
                      token: "Newline+"
                      value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                        range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                          begin: 3
                          end: 4
                    phrase: "Newline+"
                  phrase: "(Word | Newline+)"
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[2, 1] (4)"
                        end: "[2, 4] (7)"
                      token: "Word"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(4, 7), match='two'>"
                    phrase: "Word"
                  phrase: "(Word | Newline+)"
              phrase: "{(Word | Newline+), 2, 4}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[2, 4] (7)"
            success: true
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
def test_parseReturnsNone(parse_mock):
    # ----------------------------------------------------------------------
    class NonePhrase(Phrase):
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

    phrase = RepeatPhrase(NonePhrase("None Phrase"), 1, None)

    result = phrase.Lex(("root", ), CreateIterator("test"), parse_mock)
    assert result is None

# ----------------------------------------------------------------------
@pytest.mark.asyncio
def test_OnInternalPhrase(parse_mock):
    parse_mock.OnInternalPhrase = CoroutineMock(return_value=False)

    Phrase = RepeatPhrase(TokenPhrase(NewlineToken()), 1, None)

    result = Phrase.Lex(
        ("root", ),
        CreateIterator(
            textwrap.dedent(
                """\




                """,
            ),
        ),
        parse_mock,
    )

    assert str(result) == textwrap.dedent(
        """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data:
                - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    is_ignored: false
                    iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                      begin: "[1, 1] (0)"
                      end: "[5, 1] (4)"
                    token: "Newline+"
                    value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                      range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                        begin: 0
                        end: 4
                  phrase: "Newline+"
              phrase: "{Newline+, 1, None}"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[5, 1] (4)"
            success: true
        """,
    )
