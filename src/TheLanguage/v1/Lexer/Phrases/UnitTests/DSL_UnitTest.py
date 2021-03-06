# ----------------------------------------------------------------------
# |
# |  DSL_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-24 16:43:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for PhraseDSL.py"""

import os
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

    from ...Components.Tokens import (
        DedentToken,
        IndentToken,
        NewlineToken,
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
    )

    from ...Components.UnitTests import (
        Mock,
        CreateIterator,
        parse_mock,
        MethodCallsToString,
    )


# ----------------------------------------------------------------------
_word_token                                 = RegexToken("Word Token", re.compile(r"(?P<value>[a-z]+)"))
_number_token                               = RegexToken("Number Token", re.compile(r"(?P<value>\d+)"))
_upper_token                                = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
_lpar_token                                 = RegexToken("lpar", re.compile(r"\("))
_rpar_token                                 = RegexToken("rpar", re.compile(r"\)"))

# ----------------------------------------------------------------------
class TestLexSimple(object):
    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=[
            _word_token,
            _word_token,
            NewlineToken(),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleSpaceSep(self, parse_mock):
        iter = CreateIterator("one two")

        assert str(iter) == "[1, 1] (0)"

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)", "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (8)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleSpaceSep(self, parse_mock):
        iter = CreateIterator("one      two")

        assert str(iter) == "[1, 1] (0)"

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)", "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (13)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TabSep(self, parse_mock):
        iter = CreateIterator("one\ttwo")

        assert str(iter) == "[1, 1] (0)"

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (8)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultiTabSep(self, parse_mock):
        iter = CreateIterator("one\t\ttwo")

        assert str(iter) == "[1, 1] (0)"

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (9)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TrailingSpace(self, parse_mock):
        iter = CreateIterator("one two ")

        assert str(iter) == "[1, 1] (0)"

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (9)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleTrailingSpace(self, parse_mock):
        iter = CreateIterator("one two    ")

        assert str(iter) == "[1, 1] (0)"

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (12)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TrailingTab(self, parse_mock):
        iter = CreateIterator("one two\t")

        assert str(iter) == "[1, 1] (0)"

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (9)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleTrailingTab(self, parse_mock):
        iter = CreateIterator("one two\t\t\t\t")

        assert str(iter) == "[1, 1] (0)"
        assert iter.content_length == 12

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (12)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleLines(self, parse_mock):
        iter = CreateIterator(
            textwrap.dedent(
                """\
                one two
                three four
                """,
            ),
        )

        # Line 1
        assert str(iter) == "[1, 1] (0)"
        assert iter.content_length == 19

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[2, 1] (8)", "The result iterator should be modified"

        CompareResultsFromFile(str(result), suffix=".line1")
        assert len(parse_mock.method_calls) == 12

        iter = result.iter_range.end

        # Line 2
        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[2, 1] (8)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[3, 1] (19)", "The result iterator should be modified"

        CompareResultsFromFile(str(result), suffix=".line2")
        assert len(parse_mock.method_calls) == 24
        assert result.iter_range.end.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TrailingWhitespace(self, parse_mock):
        iter = CreateIterator("one two\n\n  \n    \n")

        assert str(iter) == "[1, 1] (0)"
        assert iter.content_length == 17

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[5, 1] (17)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        iter = CreateIterator("one two three")

        assert str(iter) == "[1, 1] (0)"
        assert iter.content_length == 14

        result = self._phrase.Lex(("root", ), iter, parse_mock)
        assert str(iter) == "[1, 1] (0)",  "The incoming iterator should not be modified"
        assert str(result.iter_range.end) == "[1, 8] (7)", "The result iterator should be modified"

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 10


# ----------------------------------------------------------------------
class TestLexIndentAndDedent(object):
    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=[
            _word_token,
            NewlineToken(),
            IndentToken(),
            _word_token,
            NewlineToken(),
            _word_token,
            NewlineToken(),
            DedentToken(),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
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
            single_threaded=True,
        )

        assert result.iter_range.end.AtEnd()
        CompareResultsFromFile(str(result), suffix=".results")
        CompareResultsFromFile(MethodCallsToString(parse_mock), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
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

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 19

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_FinishEarly(self, parse_mock):
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

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 8


# ----------------------------------------------------------------------
class TestIgnoreWhitespace(object):
    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=[
            _word_token,
            _lpar_token,
            PushIgnoreWhitespaceControlToken(),
            _word_token,
            _word_token,
            _word_token,
            _word_token,
            PopIgnoreWhitespaceControlToken(),
            _rpar_token,
            _word_token,
            NewlineToken(),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchNoExtra(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    one (


                        two

                            three
                        four
                            five

                    ) six
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 30


# ----------------------------------------------------------------------
class TestEmbeddedPhrases(object):
    _inner_phrase                           = CreatePhrase(
        name="Inner",
        item=[
            _word_token,
            _word_token,
        ],
    )

    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=[
            _lpar_token,
            _inner_phrase,
            _rpar_token,
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator("( one two )"),
            parse_mock,
            single_threaded=True,
        )

        CompareResultsFromFile(str(result), suffix=".results")
        CompareResultsFromFile(MethodCallsToString(parse_mock), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchAllInner(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("( one two"), parse_mock)

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 16

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchPartialInner(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("( one"), parse_mock)

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 12

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatchFirstOnly(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("( "), parse_mock)

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 9


# ----------------------------------------------------------------------
class TestDynamicPhrases(object):
    _word_phrase                            = CreatePhrase(
        name="Word Phrase",
        item=[
            _word_token,
            _word_token,
            NewlineToken(),
        ],
    )

    _number_phrase                          = CreatePhrase(
        name="Number Phrase",
        item=[
            _number_token,
            NewlineToken(),
        ],
    )

    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=[
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Expressions,
        ],
    )

    # ----------------------------------------------------------------------
    @staticmethod
    @pytest.fixture
    def modified_parse_mock(parse_mock):
        parse_mock.GetDynamicPhrases.side_effect = lambda unique_id, value: (0, [TestDynamicPhrases._word_phrase, TestDynamicPhrases._number_phrase] if value == DynamicPhrasesType.Statements else [TestDynamicPhrases._number_phrase], None)

        return parse_mock

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, modified_parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda wordb
                    123
                    456
                    """,
                ),
            ),
            modified_parse_mock,
            single_threaded=True,
        )

        CompareResultsFromFile(str(result), suffix=".results")
        assert result.iter_range.end.AtEnd()
        CompareResultsFromFile(MethodCallsToString(modified_parse_mock), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, modified_parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda wordb
                    123
                    wordc wordd
                    """,
                ),
            ),
            modified_parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert len(modified_parse_mock.method_calls) == 54


# ----------------------------------------------------------------------
class TestOrPhrases(object):
    _word_phrase                            = CreatePhrase(
        name="Word Phrase",
        item=[
            _word_token,
            NewlineToken(),
        ],
    )

    _number_phrase                          = CreatePhrase(
        name="Number Phrase",
        item=[
            _number_token,
            NewlineToken(),
        ],
    )

    _upper_phrase                           = CreatePhrase(
        name="Upper Phrase",
        item=[
            _upper_token,
            NewlineToken(),
        ],
    )

    _phrase                                 = CreatePhrase(
        item=(
            _word_phrase,
            _number_phrase,
            _upper_phrase,
        ),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_WordMatch(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("word"), parse_mock)

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 20

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NumberMatch(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("1234"), parse_mock)

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 20

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_UpperMatch(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("WORD"), parse_mock)

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 20

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator("this is not a match"),
            parse_mock,
            single_threaded=True,
        )

        CompareResultsFromFile(str(result), suffix=".results")
        CompareResultsFromFile(MethodCallsToString(parse_mock), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EarlyTermination(self, parse_mock):
        parse_mock.OnInternalPhrase = Mock(
            side_effect=[True, False],
        )

        result = self._phrase.Lex(("root", ), CreateIterator("word"), parse_mock)

        assert result is None
        assert len(parse_mock.method_calls) == 18


# ----------------------------------------------------------------------
class TestEmbeddedOrPhrases(object):
    _phrase                                 = CreatePhrase(
        (
            [_word_token, NewlineToken()],
            [_number_token, NewlineToken()],
            [_upper_token, NewlineToken()],
        ),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Standard(self, parse_mock):
        iter = CreateIterator(
            textwrap.dedent(
                """\
                one
                2222
                THREE
                """,
            ),
        )

        # Line 1
        result = self._phrase.Lex(("root", ), iter, parse_mock)
        CompareResultsFromFile(str(result), suffix=".line1")
        iter = result.iter_range.end

        # Line 2
        result = self._phrase.Lex(("root", ), iter, parse_mock)
        CompareResultsFromFile(str(result), suffix=".line2")
        iter = result.iter_range.end

        # Line 3
        result = self._phrase.Lex(("root", ), iter, parse_mock)
        CompareResultsFromFile(str(result), suffix=".line3")
        iter = result.iter_range.end

        # Done
        assert iter.AtEnd()


# ----------------------------------------------------------------------
class TestRepeatPhrases(object):
    _phrase                                 = CreatePhrase(
        [
            ZeroOrMorePhraseItem([_word_token, NewlineToken()]),
            OneOrMorePhraseItem([_number_token, NewlineToken()]),
            OptionalPhraseItem([_upper_token, NewlineToken()]),
            OneOrMorePhraseItem([_word_token, NewlineToken()]),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match1(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    wordb
                    12
                    3456
                    UPPER
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 95

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match2(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    12
                    3456
                    UPPER
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 77

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match3(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    12
                    3456
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()
        assert len(parse_mock.method_calls) == 81

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match4(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    12
                    3456
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
            single_threaded=True,
        )

        CompareResultsFromFile(str(result), suffix=".results")
        assert result.iter_range.end.AtEnd()
        CompareResultsFromFile(MethodCallsToString(parse_mock), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch1(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    wordb
                    UPPER
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 33

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch2(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    12
                    3456
                    UPPER
                    999
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 52

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EarlyTermination(self, parse_mock):
        parse_mock.OnInternalPhrase = Mock(
            side_effect=[True, True, True, True, False],
        )

        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    wordb
                    12
                    3456
                    wordc
                    wordd
                    worde
                    """,
                ),
            ),
            parse_mock,
        )

        assert result is None


# ----------------------------------------------------------------------
class TestRepeatSimilarPhrases(object):
    # Ensure that the first phrase doesn't eat the word so that it isn't available to the
    # second phrase.
    _phrase                                 = CreatePhrase(
        item=[
            ZeroOrMorePhraseItem(
                name="Word & Number",
                item=[_word_token, _number_token],
            ),
            OptionalPhraseItem(
                item=_word_token,
            ),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_LargeMatch(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("word 123"), parse_mock)

        CompareResultsFromFile(str(result))
        # assert result.iter_range.end.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SmallMatch(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("word"), parse_mock)

        CompareResultsFromFile(str(result))
        # assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
class TestNamedPhrases(object):
    _word_line_phrase                       = CreatePhrase(
        name="Word Line",
        item=[_word_token, NewlineToken()],
    )

    _phrase                                 = CreatePhrase(
        name="__Phrase__",
        item=[
            PhraseItem(name="__Dynamic__", item=DynamicPhrasesType.Statements),
            PhraseItem(
                name="__Or__",
                item=(
                    _word_line_phrase,
                    PhraseItem(name="Upper Line", item=[_upper_token, NewlineToken()]),
                ),
            ),
            CustomArityPhraseItem(
                name="__Repeat__",
                item=[_number_token, NewlineToken()],
                min_value=2,
                max_value=2,
            ),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.fixture
    def modified_parse_mock(self, parse_mock):
        parse_mock.GetDynamicPhrases.side_effect = lambda unique_id, value: (0, [self._word_line_phrase], None)

        return parse_mock

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, modified_parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    WORDB
                    123
                    456
                    """,
                ),
            ),
            modified_parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, modified_parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    worda
                    WORDB
                    123
                    """,
                ),
            ),
            modified_parse_mock,
        )

        CompareResultsFromFile(str(result))


# ----------------------------------------------------------------------
class TestComments(object):
    _multiline_phrase                       = CreatePhrase(
        OneOrMorePhraseItem(
            name="Multiline",
            item=[
                [_word_token, NewlineToken()],
                [_upper_token, NewlineToken()],
                [_number_token, NewlineToken()],
            ],
        ),
    )

    _indent_phrase                          = CreatePhrase(
        name="Indent",
        item=[
            _word_token,
            RegexToken("Colon", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            [_upper_token, NewlineToken()],
            [_number_token, NewlineToken()],
            DedentToken(),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Multiline(self, parse_mock):
        result = self._multiline_phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    one # Comment 1
                    TWO
                    3
                    four
                    FIVE                    # Comment 5
                    66
                    seven
                    EIGHT
                    999     # Comment 9
                    ten      # Comment 10
                    ELEVEN   # Comment 11
                    12       # Comment 12
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Indent(self, parse_mock):
        iterator = CreateIterator(
            textwrap.dedent(
                """\
                one:  # Comment 1
                    TWO
                    3
                four:
                    FIVE # Comment 5
                    66
                seven:
                    EIGHT
                    999                     # Comment 9
                ten:            # Comment 10
                    ELEVEN      # Comment 11
                    12          # Comment 12
                """,
            ),
        )

        # 1-3
        result = self._indent_phrase.Lex(("root", ), iterator, parse_mock)
        CompareResultsFromFile(str(result), suffix=".section1")
        iterator = result.iter_range.end

        # 4-6
        result = self._indent_phrase.Lex(("root", ), iterator, parse_mock)
        CompareResultsFromFile(str(result), suffix=".section2")
        iterator = result.iter_range.end

        # 7-9
        result = self._indent_phrase.Lex(("root", ), iterator, parse_mock)
        CompareResultsFromFile(str(result), suffix=".section3")

        iterator = result.iter_range.end

        # 10-12
        result = self._indent_phrase.Lex(("root", ), iterator, parse_mock)
        CompareResultsFromFile(str(result), suffix=".section4")
        iterator = result.iter_range.end

        assert result.iter_range.end.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_StandAlone(self, parse_mock):
        result = self._multiline_phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    # one
                    one     # After one

                    # TWO

                    TWO     # After TWO

                            # 3
                    3       # After 3
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
class TestRecursiveOrPhrases(object):
    _phrase                                 = CreatePhrase(
        name="Recursive Phrase",
        item=[
            _lpar_token,
            (_word_token, None),
            _rpar_token,
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoRecursion(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("( hello )"), parse_mock)

        CompareResultsFromFile(str(result))
        # assert result.iter_range.end.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleRecursion(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("((hello))"), parse_mock)

        CompareResultsFromFile(str(result))
        # assert result.iter_range.end.AtEnd()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_DoubleRecursion(self, parse_mock):
        result = self._phrase.Lex(("root", ), CreateIterator("( ( ( hello)))"), parse_mock)

        CompareResultsFromFile(str(result))
        # assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
class TestRecursiveRepeatPhrase(object):
    _phrase                                 = CreatePhrase(
        name="Recursive Phrase",
        item=[
            [_number_token, NewlineToken()],
            (
                CustomArityPhraseItem(
                    item=None,
                    min_value=1,
                    max_value=2,
                ),
                [_word_token, NewlineToken()]
            ),
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    123
                    456
                    789
                    helloa
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
class TestRecursiveSequencePhrase(object):
    _phrase                                 = CreatePhrase(
        [
            [_number_token, NewlineToken()],
            [_upper_token, NewlineToken()],
            (
                None,
                [RegexToken("Delimiter", re.compile(r"----")), NewlineToken()],
            ),
            [_word_token, NewlineToken()],
        ],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = self._phrase.Lex(
            ("root", ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    123
                    UPPERA
                    456
                    UPPERB
                    789
                    UPPERC
                    ----
                    worda
                    wordb
                    wordc
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))
        assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_IgnoreWhitespace(parse_mock):
    phrase = CreatePhrase(
        name="Phrase",
        item=[
            PushIgnoreWhitespaceControlToken(),
            _word_token,
            _word_token,
            _word_token,
            PopIgnoreWhitespaceControlToken(),
        ],
    )

    result = phrase.Lex(
        ("root", ),
        CreateIterator(
            textwrap.dedent(
                """\
                worda
                            wordb

                    wordc

                """,
            ),
        ),
        parse_mock,
    )

    CompareResultsFromFile(str(result))
    assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_IgnoreWhitespaceNestedPhrase(parse_mock):
    phrase = CreatePhrase(
        name="Phrase",
        item=[
            _word_token,
            NewlineToken(),
            CreatePhrase(
                name="Nested",
                item=[
                    PushIgnoreWhitespaceControlToken(),
                    _word_token,
                    _word_token,
                    PopIgnoreWhitespaceControlToken(),
                ],
            ),
            _word_token,
            NewlineToken(),
        ],
    )

    result = phrase.Lex(
        ("root", ),
        CreateIterator(
            textwrap.dedent(
                """\
                worda


                        wordb
                            wordc

                wordd
                """,
            ),
        ),
        parse_mock,
    )

    CompareResultsFromFile(str(result))
    assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_IgnoreWhitespaceNestedPhraseWithDedents(parse_mock):
    phrase = CreatePhrase(
        name="Phrase",
        item=[
            _word_token,
            RegexToken("':'", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            CreatePhrase(
                name="Nested",
                item=[
                    PushIgnoreWhitespaceControlToken(),
                    _word_token,
                    _word_token,
                    PopIgnoreWhitespaceControlToken(),
                ],
            ),
            _word_token,
            NewlineToken(),
            DedentToken(),
            _word_token,
            NewlineToken(),
        ],
    )

    result = phrase.Lex(
        ("root", ),
        CreateIterator(
            textwrap.dedent(
                """\
                newscope:


                    worda
                        wordb

                    wordc
                wordd
                """,
            ),
        ),
        parse_mock,
    )

    CompareResultsFromFile(str(result))
    assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_IgnoreWhitespaceNestedPhraseEndWithDedents(parse_mock):
    phrase = CreatePhrase(
        name="Phrase",
        item=[
            _word_token,
            RegexToken("':'", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            CreatePhrase(
                name="Nested",
                item=[
                    PushIgnoreWhitespaceControlToken(),
                    _word_token,
                    _word_token,
                    PopIgnoreWhitespaceControlToken(),
                ],
            ),
            DedentToken(),
        ],
    )

    result = phrase.Lex(
        ("root", ),
        CreateIterator(
            textwrap.dedent(
                """\
                newscope:


                    worda
                        wordb


                """,
            ),
        ),
        parse_mock,
    )

    CompareResultsFromFile(str(result))
    assert result.iter_range.end.AtEnd()


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_NestedPhrase(parse_mock):
    phrase = CreatePhrase(
        name="Phrase",
        item=[TokenPhrase(_word_token),],
    )

    result = phrase.Lex(("root", ), CreateIterator("test"), parse_mock)

    CompareResultsFromFile(str(result))
    # assert result.iter_range.end.AtEnd()
