# ----------------------------------------------------------------------
# |
# |  TokenPhrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-24 12:16:23
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

    from ...Components.Tokens import (
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
        result = self._word_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(0, 4), match='This'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: True
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhrase, 0, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 4), match='This'>"
                phrase: "Word"
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # <whitespace>
        whitespace = iter.GetNextWhitespaceRange()
        assert whitespace is not None
        assert whitespace.begin == iter.offset
        iter.Advance(whitespace.end - whitespace.begin)

        # is
        result = self._word_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(10, 12), match='is'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 11] (10)"
              end: "[1, 13] (12)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhrase, 10, 12
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(10, 12), match='is'>"
                phrase: "Word"
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # <whitespace>
        whitespace = iter.GetNextWhitespaceRange()
        assert whitespace is not None
        assert whitespace.begin == iter.offset
        iter.Advance(whitespace.end - whitespace.begin)

        # a
        result = self._word_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(13, 14), match='a'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 14] (13)"
              end: "[1, 15] (14)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhrase, 13, 14
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(13, 14), match='a'>"
                phrase: "Word"
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # <whitespace>
        whitespace = iter.GetNextWhitespaceRange()
        assert whitespace is not None
        assert whitespace.begin == iter.offset
        iter.Advance(whitespace.end - whitespace.begin)

        # test
        result = self._word_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(20, 24), match='test'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 21] (20)"
              end: "[1, 25] (24)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhrase, 20, 24
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(20, 24), match='test'>"
                phrase: "Word"
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # <whitespace>
        whitespace = iter.GetNextWhitespaceRange()
        assert whitespace is None
        iter.SkipWhitespaceSuffix()

        # Newline
        result = self._newline_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 27
                    end: 28
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 28] (27)"
              end: "[2, 1] (28)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Newline+"
            1) OnInternalPhrase, 27, 28
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 27
                      end: 28
                phrase: "Newline+"
            2) EndPhrase, "Newline+" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NotAMatch(self, parse_mock):
        iter = CreateIterator("te__")

        result = self._word_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: None
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 1] (0)"
            success: False
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) EndPhrase, "Word" [False]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_IndentSimple(self, parse_mock):
        parse_mock.OnPushScope = CoroutineMock()
        parse_mock.OnPopScope = CoroutineMock()

        iter = CreateIterator(
            textwrap.dedent(
                """\
                one
                    two
                """,
            ),
        )

        # One
        result = self._word_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 4] (3)"
            success: True
            """,
        )

        assert iter.offset == 0
        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhrase, 0, 3
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                phrase: "Word"
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # Newline
        result = self._newline_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 3
                    end: 4
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 4] (3)"
              end: "[2, 1] (4)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Newline+"
            1) OnInternalPhrase, 3, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 3
                      end: 4
                phrase: "Newline+"
            2) EndPhrase, "Newline+" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # Indent
        result = self._indent_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Indent"
                value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                  indent_value: 4
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 4
                    end: 8
              phrase: "Indent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[2, 1] (4)"
              end: "[2, 5] (8)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Indent"
            1) OnPushScope, 4, 8
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Indent"
                  value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                    indent_value: 4
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 4
                      end: 8
                phrase: "Indent"
            2) EndPhrase, "Indent" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # two
        result = self._word_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(8, 11), match='two'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[2, 5] (8)"
              end: "[2, 8] (11)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhrase, 8, 11
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(8, 11), match='two'>"
                phrase: "Word"
            2) EndPhrase, "Word" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # Newline
        result = self._newline_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 11
                    end: 12
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[2, 8] (11)"
              end: "[3, 1] (12)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd() == False

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Newline+"
            1) OnInternalPhrase, 11, 12
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 11
                      end: 12
                phrase: "Newline+"
            2) EndPhrase, "Newline+" [True]
            """,
        )

        iter = result.iter_range.end
        parse_mock.reset_mock()

        # Dedent
        result = self._dedent_phrase.Lex(("root", ), iter, parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Dedent"
                value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                  {}
              phrase: "Dedent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[3, 1] (12)"
              end: "[3, 1] (12)"
            success: True
            """,
        )

        assert result.iter_range.end.AtEnd()

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Dedent"
            1) OnPopScope, 12, 12
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Dedent"
                  value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                    {}
                phrase: "Dedent"
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
            None,
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
            if expected_phrase is None:
                iter.SkipWhitespacePrefix()
                continue

            results.append(expected_phrase.Lex(("root", ), iter, parse_mock))
            iter = results[-1].iter_range.end.Clone()

        assert iter.AtEnd()

        assert "\n".join([str(result) for result in results]) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 4] (3)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 3
                    end: 4
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 4] (3)"
              end: "[2, 1] (4)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Indent"
                value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                  indent_value: 4
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 4
                    end: 8
              phrase: "Indent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[2, 1] (4)"
              end: "[2, 5] (8)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(8, 11), match='two'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[2, 5] (8)"
              end: "[2, 8] (11)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 11
                    end: 12
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[2, 8] (11)"
              end: "[3, 1] (12)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Indent"
                value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                  indent_value: 8
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 12
                    end: 20
              phrase: "Indent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[3, 1] (12)"
              end: "[3, 9] (20)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(20, 25), match='three'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[3, 9] (20)"
              end: "[3, 14] (25)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 25
                    end: 26
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[3, 14] (25)"
              end: "[4, 1] (26)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(34, 38), match='four'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[4, 9] (34)"
              end: "[4, 13] (38)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 38
                    end: 39
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[4, 13] (38)"
              end: "[5, 1] (39)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Dedent"
                value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                  {}
              phrase: "Dedent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[5, 1] (39)"
              end: "[5, 5] (43)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(43, 47), match='five'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[5, 5] (43)"
              end: "[5, 9] (47)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 47
                    end: 48
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[5, 9] (47)"
              end: "[6, 1] (48)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Indent"
                value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                  indent_value: 12
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 48
                    end: 60
              phrase: "Indent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[6, 1] (48)"
              end: "[6, 13] (60)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(60, 63), match='six'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[6, 13] (60)"
              end: "[6, 16] (63)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 63
                    end: 64
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[6, 16] (63)"
              end: "[7, 1] (64)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Dedent"
                value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                  {}
              phrase: "Dedent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[7, 1] (64)"
              end: "[7, 5] (68)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(68, 73), match='seven'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[7, 5] (68)"
              end: "[7, 10] (73)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 73
                    end: 74
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[7, 10] (73)"
              end: "[8, 1] (74)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Indent"
                value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                  indent_value: 8
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 74
                    end: 82
              phrase: "Indent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[8, 1] (74)"
              end: "[8, 9] (82)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Word"
                value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                  match: "<_sre.SRE_Match object; span=(82, 87), match='eight'>"
              phrase: "Word"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[8, 9] (82)"
              end: "[8, 14] (87)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Newline+"
                value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                  range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                    begin: 87
                    end: 88
              phrase: "Newline+"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[8, 14] (87)"
              end: "[9, 1] (88)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Dedent"
                value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                  {}
              phrase: "Dedent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[9, 1] (88)"
              end: "[9, 1] (88)"
            success: True

            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                is_ignored: False
                token: "Dedent"
                value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                  {}
              phrase: "Dedent"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[9, 1] (88)"
              end: "[9, 1] (88)"
            success: True
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Word"
            1) OnInternalPhrase, 0, 3
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 3), match='one'>"
                phrase: "Word"
            2) EndPhrase, "Word" [True]
            3) StartPhrase, "Newline+"
            4) OnInternalPhrase, 3, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 3
                      end: 4
                phrase: "Newline+"
            5) EndPhrase, "Newline+" [True]
            6) StartPhrase, "Indent"
            7) OnPushScope, 4, 8
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Indent"
                  value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                    indent_value: 4
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 4
                      end: 8
                phrase: "Indent"
            8) EndPhrase, "Indent" [True]
            9) StartPhrase, "Word"
            10) OnInternalPhrase, 8, 11
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(8, 11), match='two'>"
                phrase: "Word"
            11) EndPhrase, "Word" [True]
            12) StartPhrase, "Newline+"
            13) OnInternalPhrase, 11, 12
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 11
                      end: 12
                phrase: "Newline+"
            14) EndPhrase, "Newline+" [True]
            15) StartPhrase, "Indent"
            16) OnPushScope, 12, 20
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Indent"
                  value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                    indent_value: 8
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 12
                      end: 20
                phrase: "Indent"
            17) EndPhrase, "Indent" [True]
            18) StartPhrase, "Word"
            19) OnInternalPhrase, 20, 25
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(20, 25), match='three'>"
                phrase: "Word"
            20) EndPhrase, "Word" [True]
            21) StartPhrase, "Newline+"
            22) OnInternalPhrase, 25, 26
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 25
                      end: 26
                phrase: "Newline+"
            23) EndPhrase, "Newline+" [True]
            24) StartPhrase, "Word"
            25) OnInternalPhrase, 34, 38
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(34, 38), match='four'>"
                phrase: "Word"
            26) EndPhrase, "Word" [True]
            27) StartPhrase, "Newline+"
            28) OnInternalPhrase, 38, 39
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 38
                      end: 39
                phrase: "Newline+"
            29) EndPhrase, "Newline+" [True]
            30) StartPhrase, "Dedent"
            31) OnPopScope, 39, 43
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Dedent"
                  value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                    {}
                phrase: "Dedent"
            32) EndPhrase, "Dedent" [True]
            33) StartPhrase, "Word"
            34) OnInternalPhrase, 43, 47
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(43, 47), match='five'>"
                phrase: "Word"
            35) EndPhrase, "Word" [True]
            36) StartPhrase, "Newline+"
            37) OnInternalPhrase, 47, 48
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 47
                      end: 48
                phrase: "Newline+"
            38) EndPhrase, "Newline+" [True]
            39) StartPhrase, "Indent"
            40) OnPushScope, 48, 60
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Indent"
                  value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                    indent_value: 12
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 48
                      end: 60
                phrase: "Indent"
            41) EndPhrase, "Indent" [True]
            42) StartPhrase, "Word"
            43) OnInternalPhrase, 60, 63
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(60, 63), match='six'>"
                phrase: "Word"
            44) EndPhrase, "Word" [True]
            45) StartPhrase, "Newline+"
            46) OnInternalPhrase, 63, 64
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 63
                      end: 64
                phrase: "Newline+"
            47) EndPhrase, "Newline+" [True]
            48) StartPhrase, "Dedent"
            49) OnPopScope, 64, 68
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Dedent"
                  value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                    {}
                phrase: "Dedent"
            50) EndPhrase, "Dedent" [True]
            51) StartPhrase, "Word"
            52) OnInternalPhrase, 68, 73
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(68, 73), match='seven'>"
                phrase: "Word"
            53) EndPhrase, "Word" [True]
            54) StartPhrase, "Newline+"
            55) OnInternalPhrase, 73, 74
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 73
                      end: 74
                phrase: "Newline+"
            56) EndPhrase, "Newline+" [True]
            57) StartPhrase, "Indent"
            58) OnPushScope, 74, 82
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Indent"
                  value: # <class 'v1.Lexer.Components.Tokens.IndentToken.MatchResult'>
                    indent_value: 8
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 74
                      end: 82
                phrase: "Indent"
            59) EndPhrase, "Indent" [True]
            60) StartPhrase, "Word"
            61) OnInternalPhrase, 82, 87
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Word"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(82, 87), match='eight'>"
                phrase: "Word"
            62) EndPhrase, "Word" [True]
            63) StartPhrase, "Newline+"
            64) OnInternalPhrase, 87, 88
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Newline+"
                  value: # <class 'v1.Lexer.Components.Tokens.NewlineToken.MatchResult'>
                    range: # <class 'v1.Lexer.Components.Normalize.OffsetRange'>
                      begin: 87
                      end: 88
                phrase: "Newline+"
            65) EndPhrase, "Newline+" [True]
            66) StartPhrase, "Dedent"
            67) OnPopScope, 88, 88
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Dedent"
                  value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                    {}
                phrase: "Dedent"
            68) EndPhrase, "Dedent" [True]
            69) StartPhrase, "Dedent"
            70) OnPopScope, 88, 88
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: False
                  token: "Dedent"
                  value: # <class 'v1.Lexer.Components.Tokens.DedentToken.MatchResult'>
                    {}
                phrase: "Dedent"
            71) EndPhrase, "Dedent" [True]
            """,
        )
