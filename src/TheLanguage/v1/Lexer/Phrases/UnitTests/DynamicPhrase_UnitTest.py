# ----------------------------------------------------------------------
# |
# |  DynamicPhrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-24 15:22:02
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
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import CompareResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..DSL import *
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
            lambda *args, **kwargs: (0, [self._lower_phrase], None),
        )

        result = phrase.Lex(("root", ), CreateIterator("word"), parse_mock)
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
                phrase: "(lower)"
              phrase: "Dynamic Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: true
            """,
        )

        assert len(parse_mock.method_calls) == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleNoMatch(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (0, [self._lower_phrase], None),
        )

        result = phrase.Lex(("root", ), CreateIterator("1234"), parse_mock)
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data:
                  - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: null
                    phrase: "lower"
                phrase: "(lower)"
              phrase: "Dynamic Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 1] (0)"
            success: false
            """,
        )

        assert len(parse_mock.method_calls) == 6

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleNumber(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (0, [self._lower_phrase, self._number_phrase], None),
        )

        result = phrase.Lex(("root", ), CreateIterator("1234"), parse_mock)
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
                    token: "number"
                    value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                      match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                  phrase: "number"
                phrase: "(lower | number)"
              phrase: "Dynamic Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: true
            """,
        )

        assert len(parse_mock.method_calls) == 11

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleLower(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (0, [self._lower_phrase, self._number_phrase], None),
        )

        result = phrase.Lex(("root", ), CreateIterator("word"), parse_mock)
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
              phrase: "Dynamic Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: true
            """,
        )

        assert len(parse_mock.method_calls) == 11

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleNumberEvents(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (0, [self._lower_phrase, self._number_phrase], None),
        )

        result = phrase.Lex(
            ("root", ),
            CreateIterator("1234"),
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
                    token: "number"
                    value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                      match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                  phrase: "number"
                phrase: "(lower | number)"
              phrase: "Dynamic Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 5] (4)"
            success: true
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Dynamic Phrase"
            1) StartPhrase, "(lower | number)"
            2) StartPhrase, "lower"
            3) EndPhrase, "lower" [False]
            4) StartPhrase, "number"
            5) OnInternalPhrase, 0, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                  is_ignored: false
                  iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                    begin: "[1, 1] (0)"
                    end: "[1, 5] (4)"
                  token: "number"
                  value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                    match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                phrase: "number"
            6) EndPhrase, "number" [True]
            7) OnInternalPhrase, 0, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                    is_ignored: false
                    iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                      begin: "[1, 1] (0)"
                      end: "[1, 5] (4)"
                    token: "number"
                    value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                      match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                  phrase: "number"
                phrase: "(lower | number)"
            8) EndPhrase, "(lower | number)" [True]
            9) OnInternalPhrase, 0, 4
                # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                  data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: # <class 'v1.Lexer.Components.Phrase.Phrase.TokenLexResultData'>
                      is_ignored: false
                      iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
                        begin: "[1, 1] (0)"
                        end: "[1, 5] (4)"
                      token: "number"
                      value: # <class 'v1.Lexer.Components.Tokens.RegexToken.MatchResult'>
                        match: "<_sre.SRE_Match object; span=(0, 4), match='1234'>"
                    phrase: "number"
                  phrase: "(lower | number)"
                phrase: "Dynamic Phrase"
            10) EndPhrase, "Dynamic Phrase" [True]
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleNoMatchEvents(self, parse_mock):
        phrase = DynamicPhrase(
            DynamicPhrasesType.Statements,
            lambda *args, **kwargs: (0, [self._lower_phrase], None),
        )

        result = phrase.Lex(
            ("root", ),
            CreateIterator("1234"),
            parse_mock,
            single_threaded=True,
        )
        assert str(result) == textwrap.dedent(
            """\
            # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
            data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
              data: # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                data:
                  - # <class 'v1.Lexer.Components.Phrase.Phrase.LexResultData'>
                    data: null
                    phrase: "lower"
                phrase: "(lower)"
              phrase: "Dynamic Phrase"
            iter_range: # <class 'v1.Lexer.Components.Phrase.Phrase.NormalizedIteratorRange'>
              begin: "[1, 1] (0)"
              end: "[1, 1] (0)"
            success: false
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) StartPhrase, "Dynamic Phrase"
            1) StartPhrase, "(lower)"
            2) StartPhrase, "lower"
            3) EndPhrase, "lower" [False]
            4) EndPhrase, "(lower)" [False]
            5) EndPhrase, "Dynamic Phrase" [False]
            """,
        )


# ----------------------------------------------------------------------
class TestLeftRecursiveSemicolonSuffix(object):
    _phrases                                = [
        CreatePhrase(RegexToken("Lower", re.compile(r"(?P<value>[a-z_]+[0-9]*)"))),
        CreatePhrase(RegexToken("Upper", re.compile(r"(?P<value>[A-Z_]+[0-9]*)"))),
        CreatePhrase(name="Add", item=[DynamicPhrasesType.Statements, "+", DynamicPhrasesType.Statements, ";"]),
        CreatePhrase(name="Sub", item=[DynamicPhrasesType.Statements, "-", DynamicPhrasesType.Statements, ";"]),
        CreatePhrase(name="Mul", item=[DynamicPhrasesType.Statements, "*", DynamicPhrasesType.Statements, ";"]),
        CreatePhrase(name="Div", item=[DynamicPhrasesType.Statements, "/", DynamicPhrasesType.Statements, ";"]),
        CreatePhrase(name="Ter", item=[DynamicPhrasesType.Statements, "if", DynamicPhrasesType.Statements, "else", DynamicPhrasesType.Statements]),
        CreatePhrase(name="Index", item=[DynamicPhrasesType.Statements, "[", DynamicPhrasesType.Statements, "]"]),
    ]

    _phrase                                 = DynamicPhrase(
        DynamicPhrasesType.Statements,
        lambda unique_id, dynamic_phrases_type, observer: observer.GetDynamicPhrases(unique_id, dynamic_phrases_type),
    )

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def parse_mock_ex(cls, parse_mock):
        # ----------------------------------------------------------------------
        def GetDynamicPhrases(*args, **kwargs):
            return 0, cls._phrases, "All Phrases"

        # ----------------------------------------------------------------------

        parse_mock.GetDynamicPhrases = GetDynamicPhrases

        return parse_mock

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_3Items1(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + TWO - three;;"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_3Items2(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + TWO; - three;"),
                    parse_mock_ex,
                ),
            ),
        )


# ----------------------------------------------------------------------
def TestLeftRecursivePrecedenceFunc(
    data: Phrase.LexResultData,
) -> int:
    if data.phrase.name in ["Add", "Sub"]:
        return 1000
    if data.phrase.name in ["Mul", "Div"]:
        return 100
    if data.phrase.name in ["Ter"]:
        return 10
    if data.phrase.name in ["Index", "Neg"]:
        return 1

    assert False, data.phrase.name


# ----------------------------------------------------------------------
class TestLeftRecursive(object):
    _phrases                                = [
        CreatePhrase(
            RegexToken("Lower", re.compile(r"(?P<value>[a-z_]+[0-9]*)")),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
        CreatePhrase(
            RegexToken("Upper", re.compile(r"(?P<value>[A-Z_]+[0-9]*)")),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
        CreatePhrase(
            PhraseItem(
                name="Add",
                item=[DynamicPhrasesType.Statements, "+", DynamicPhrasesType.Statements],
            ),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
        CreatePhrase(
            PhraseItem(
                name="Sub",
                item=[DynamicPhrasesType.Statements, "-", DynamicPhrasesType.Statements],
            ),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
        CreatePhrase(
            PhraseItem(
                name="Mul",
                item=[DynamicPhrasesType.Statements, "*", DynamicPhrasesType.Statements],
            ),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
        CreatePhrase(
            PhraseItem(
                name="Div",
                item=[DynamicPhrasesType.Statements, "/", DynamicPhrasesType.Statements],
            ),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
        CreatePhrase(
            PhraseItem(
                name="Ter",
                item=[DynamicPhrasesType.Statements, "if", DynamicPhrasesType.Statements, "else", DynamicPhrasesType.Statements],
            ),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
        CreatePhrase(
            PhraseItem(
                name="Index",
                item=[DynamicPhrasesType.Statements, "[", DynamicPhrasesType.Statements, "]"],
            ),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
        CreatePhrase(
            PhraseItem(
                name="Neg",
                item=["-", DynamicPhrasesType.Statements],
            ),
            precedence_func=TestLeftRecursivePrecedenceFunc,
        ),
    ]

    # ----------------------------------------------------------------------
    _phrase                                 = DynamicPhrase(
        DynamicPhrasesType.Statements,
        get_dynamic_phrases_func=lambda unique_id, dynamic_phrases_type, observer: observer.GetDynamicPhrases(unique_id, dynamic_phrases_type),
        precedence_func=TestLeftRecursivePrecedenceFunc,
    )

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def parse_mock_ex(cls, parse_mock):
        # ----------------------------------------------------------------------
        def GetDynamicPhrases(*args, **kwargs):
            return 0, cls._phrases, "All Phrases"

        # ----------------------------------------------------------------------

        parse_mock.GetDynamicPhrases = GetDynamicPhrases

        return parse_mock

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock_ex):
        # No match, as we are explicitly asking for a left-recursive match
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("!!this_will_not_match!!"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleWord(self, parse_mock_ex):
        # This will match, as we can have either a single word or a left-recursive match
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("this_will_match"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Simple(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + TWO"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_3Items(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + TWO - three"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_3ItemsWithIndexes(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one[a][b][c][d] + TWO[e][f][g] - three[h][i]"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_4Items(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + TWO - three * FOUR"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_5Items(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + TWO - three * FOUR / five"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_1Index(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("var[a]"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_2Indexes(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("var[a][b]"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ManyIndexes(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("var[a][b][c][d][e][f][g]"),
                    parse_mock_ex,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Complicated1(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + true if CONDITION else false - three[a][b][c][d] * FOUR"),
                    parse_mock_ex,
                    single_threaded=True,
                ),
            ),
            suffix=".results",
        )

        CompareResultsFromFile(MethodCallsToString(parse_mock_ex), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Complicated2(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + var[a][b][c] + three + four if CONDITION else five"),
                    parse_mock_ex,
                    single_threaded=True,
                ),
            ),
            suffix=".results",
        )

        CompareResultsFromFile(MethodCallsToString(parse_mock_ex), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Complicated3(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("TRUE if var[a][one if CONDITION else two] else FALSE"),
                    parse_mock_ex,
                    single_threaded=True,
                ),
            ),
            suffix=".results",
        )

        CompareResultsFromFile(MethodCallsToString(parse_mock_ex), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Expr1(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + two * three + four"),
                    parse_mock_ex,
                    single_threaded=True,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Expr2(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one * two * three + four"),
                    parse_mock_ex,
                    single_threaded=True,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Expr3(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + two * six / three + five"),
                    parse_mock_ex,
                    single_threaded=True,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Expr4(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one + two[a] * three"),
                    parse_mock_ex,
                    single_threaded=True,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Expr5(self, parse_mock_ex):
        CompareResultsFromFile(
            str(
                self._phrase.Lex(
                    ("root", ),
                    CreateIterator("one * two[a] * three"),
                    parse_mock_ex,
                    single_threaded=True,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NegativeTest(self, parse_mock_ex):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator("-one + two"),
            parse_mock_ex,
            single_threaded=True,
        )

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NegativeTest2(self, parse_mock_ex):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator("-one * two + three - -four"),
            parse_mock_ex,
            single_threaded=True,
        )
