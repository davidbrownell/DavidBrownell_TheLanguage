# ----------------------------------------------------------------------
# |
# |  TranslationUnitParser_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-01 15:39:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for TranslationUnit.py"""

import os
import re
import textwrap

import pytest

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TranslationUnitParser import *

    from ..Components.AST import Node

    from ..Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )

    from ..Components.UnitTests import (
        CoroutineMock,
        CreateIterator,
        MethodCallsToString,
        parse_mock as parse_mock_impl,
    )

    from ..Phrases.DSL import CreatePhrase, DynamicPhrasesType


# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock(parse_mock_impl):
    parse_mock_impl.OnPhraseCompleteAsync = CoroutineMock()

    return parse_mock_impl

# ----------------------------------------------------------------------
_upper_token                                = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
_lower_token                                = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
_number_token                               = RegexToken("Number", re.compile(r"(?P<value>\d+)"))

# ----------------------------------------------------------------------
class TestSimple(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number Phrase", item=[_number_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo(
        [],
        [],
        [_upper_phrase, _lower_phrase, _number_phrase],
        [],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchStandard(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                    two
                    33333
                    """,
                ),
            ),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == ResultsFromFile(".results")
        assert MethodCallsToString(parse_mock) == ResultsFromFile(".events")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchReverse(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    33
                    twooooooooo
                    ONE
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == ResultsFromFile()
        assert len(parse_mock.method_calls) == 15

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EarlyTermination(self, parse_mock):
        parse_mock.OnPhraseCompleteAsync = CoroutineMock(
            side_effect=[True, False],
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    33
                    twooooooooo
                    ONE
                    """,
                ),
            ),
            parse_mock,
        )

        assert result is None


# ----------------------------------------------------------------------
class TestIndentation(object):
    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=[
            _upper_token,
            NewlineToken(),
            IndentToken(),
            _upper_token,
            _upper_token,
            NewlineToken(),
            DedentToken(),
        ],
    )

    _phrases                                = DynamicPhrasesInfo([], [], [_phrase], [])

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        TWO      THREE
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == ResultsFromFile()


# ----------------------------------------------------------------------
class TestNewPhrases(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=_upper_token)
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo([], [], [_upper_phrase,], [])
    _new_phrases                            = DynamicPhrasesInfo([], [], [_lower_phrase,], [])

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnPhraseCompleteAsync = CoroutineMock(
            side_effect=[self._new_phrases, True, True, True, True, True, True, True, True],
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE two
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == ResultsFromFile()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
                self._phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE two
                        """,
                    ),
                ),
                parse_mock,
            )

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 1
        assert ex.Column == 4

        assert ex.ToDebugString() == ResultsFromFile()


# ----------------------------------------------------------------------
class TestNewScopedPhrases(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=_upper_token)
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=_lower_token)

    _newline_phrase                         = CreatePhrase(name="Newline Phrase", item=NewlineToken())
    _indent_phrase                          = CreatePhrase(name="Indent Phrase", item=IndentToken())
    _dedent_phrase                          = CreatePhrase(name="Dedent Phrase", item=DedentToken())

    _phrases                                = DynamicPhrasesInfo([], [], [_upper_phrase, _newline_phrase, _indent_phrase, _dedent_phrase], [])
    _new_phrases                            = DynamicPhrasesInfo([], [], [_lower_phrase,], [])

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        two
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == ResultsFromFile()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
                self._phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE
                            two

                        nomatch
                        """,
                    ),
                ),
                parse_mock,
            )

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 4
        assert ex.Column == 1

        assert ex.ToDebugString() == ResultsFromFile()


# ----------------------------------------------------------------------
class TestNewScopedPhrasesComplex(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=_upper_token)
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=_lower_token)

    _newline_phrase                         = CreatePhrase(name="Newline Phrase", item=NewlineToken())
    _dedent_phrase                          = CreatePhrase(name="Dedent Phrase", item=DedentToken())

    _new_scope_phrase                       = CreatePhrase(
        name="New Scope",
        item=[
            _upper_token,
            RegexToken("Colon", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DedentToken(),
        ],
    )

    _phrases                             = DynamicPhrasesInfo([], [], [_newline_phrase, _new_scope_phrase], [])
    _new_phrases                         = DynamicPhrasesInfo([], [], [_upper_phrase, _lower_phrase], [])

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    NEWSCOPE:
                        UPPER

                        lower
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == ResultsFromFile()


# ----------------------------------------------------------------------
class TestEmbeddedPhrases(object):
    _upper_lower_phrase                     = CreatePhrase(name="Upper Lower Phrase", item=[_upper_token, _lower_token, NewlineToken()])

    _uul_phrase                             = CreatePhrase(name="uul", item=[_upper_token, _upper_lower_phrase])
    _lul_phrase                             = CreatePhrase(name="lul", item=[_lower_token, _upper_lower_phrase])

    _phrases                                = DynamicPhrasesInfo([], [], [_uul_phrase, _lul_phrase], [])

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE TWO  three
                    four    FIVE six
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == ResultsFromFile()


# ----------------------------------------------------------------------
class TestVariedLengthMatches(object):
    _upper_phrase                           = CreatePhrase(name="Upper", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower", item=[_lower_token, _lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number", item=[_number_token, _number_token, _number_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo(
        [],
        [],
        [_upper_phrase, _lower_phrase, _number_phrase],
        [],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    one two
                    1 2 3
                    WORD
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == ResultsFromFile()


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_EmptyDynamicPhrasesInfo(parse_mock):
    parse_mock.OnPhraseCompleteAsync = CoroutineMock(
        return_value=DynamicPhrasesInfo([], [], [], []),
    )

    result = await ParseAsync(
        DynamicPhrasesInfo(
            [],
            [],
            [
                CreatePhrase(name="Newline Phrase", item=NewlineToken()),
                CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()]),
            ],
            [],
        ),
        CreateIterator(
            textwrap.dedent(
                """\

                word
                """,
            ),
        ),
        parse_mock,
    )

    assert str(result) == ResultsFromFile()


# ----------------------------------------------------------------------
class TestPreventParentTraversal(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])
    _indent_phrase                          = CreatePhrase(name="Indent Phrase", item=IndentToken())
    _dedent_phrase                          = CreatePhrase(name="Dedent Phrase", item=DedentToken())

    _phrases                                = DynamicPhrasesInfo(
        [],
        [],
        [_upper_phrase, _indent_phrase, _dedent_phrase],
        [],
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async  def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=DynamicPhrasesInfo(
                [],
                [],
                [self._lower_phrase, self._dedent_phrase],
                [],
                False,
            ),
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        two
                        three
                        four

                    FIVE
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == ResultsFromFile()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=DynamicPhrasesInfo(
                [],
                [],
                [self._lower_phrase, self._dedent_phrase],
                [],
                False,
            ),
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
                self._phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE
                            two
                            three
                            four

                        five
                        """,
                    ),
                ),
                parse_mock,
            )

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 6
        assert ex.Column == 1

        assert ex.ToDebugString() == ResultsFromFile()


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_InvalidDynamicTraversalError(parse_mock):
    parse_mock.OnPhraseCompleteAsync = CoroutineMock(
        return_value=DynamicPhrasesInfo(
            [],
            [],
            [CreatePhrase(name="Newline", item=NewlineToken()),],
            [],
            False,
        ),
    )

    with pytest.raises(InvalidDynamicTraversalError) as ex:
        result = await ParseAsync(
            DynamicPhrasesInfo(
                [],
                [],
                [CreatePhrase(name="Newline", item=NewlineToken()),],
                [],
            ),
            CreateIterator(
                textwrap.dedent(
                    """\



                    """,
                ),
            ),
            parse_mock,
        )

        assert result is None, result

    ex = ex.value

    assert str(ex) == "Dynamic phrases that prohibit parent traversal should never be applied over other dynamic phrases within the same lexical scope; consider making these dynamic phrases the first ones applied in this lexical scope."
    assert ex.Line == 4
    assert ex.Column == 1


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_DynamicExpressions(parse_mock):
    result = await ParseAsync(
        DynamicPhrasesInfo(
            [
                CreatePhrase(
                    name="Expression",
                    item=_number_token,
                ),
            ],
            [],
            [
                CreatePhrase(
                    name="Statement",
                    item=[
                        _upper_token,
                        DynamicPhrasesType.Expressions,
                        _lower_token,
                        NewlineToken(),
                    ],
                ),
            ],
            [],
        ),
        CreateIterator("WORD 1234 lower"),
        parse_mock,
    )

    assert str(result) == ResultsFromFile()


# ----------------------------------------------------------------------
class TestCatastrophicInclude(object):
    _include_phrase                         = CreatePhrase(
        name="Include Phrase",
        item=[
            RegexToken("include", re.compile(r"include")),
            _upper_token,
            NewlineToken(),
        ],
    )

    # Both of these phrases start with an include, but the
    # dynamic phrases allowed will be based on the included
    # value.
    _lower_include_phrase                   = CreatePhrase(
        name="Lower Include Phrase",
        item=[
            _include_phrase,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
        ],
    )

    _number_include_phrase                  = CreatePhrase(
        name="Number Include Phrase",
        item=[
            _include_phrase,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
        ],
    )

    _lower_phrase                           = CreatePhrase(
        name="Lower Phrase",
        item=[
            _lower_token,
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

    _phrases                                = DynamicPhrasesInfo(
        [],
        [],
        [_lower_include_phrase, _number_include_phrase],
        [],
    )

    _lower_dynamic_phrases                  = DynamicPhrasesInfo(
        [],
        [],
        [_lower_phrase,],
        [],
        True,
        # "Lower Dynamic Phrases",
    )

    _number_dynamic_phrases                 = DynamicPhrasesInfo(
        [],
        [],
        [_number_phrase,],
        [],
        True,
        # "Number Dynamic Phrases",
    )

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def this_parse_mock(cls, parse_mock):
        # ----------------------------------------------------------------------
        async def OnPhraseCompleteAsync(
            phrase: Phrase,
            node: Node,
            iter_before: Phrase.NormalizedIterator,
            iter_after: Phrase.NormalizedIterator,
        ):
            if phrase == cls._include_phrase:
                value = node.Children[1].Value.Match.group("value")

                if value == "LOWER":
                    return cls._lower_dynamic_phrases
                elif value == "NUMBER":
                    return cls._number_dynamic_phrases
                else:
                    assert False, value

            return True

        # ----------------------------------------------------------------------

        parse_mock.OnPhraseCompleteAsync = OnPhraseCompleteAsync

        return parse_mock

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Lower(self, this_parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include LOWER
                    one
                    two
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert str(result) == ResultsFromFile()
        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_LowerAdditionalItem(self, this_parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include LOWER
                    one
                    two

                    three
                    four
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert str(result) == ResultsFromFile()
        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Number(self, this_parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include NUMBER
                    1
                    2
                    3
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert str(result) == ResultsFromFile()
        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NumberAdditionalItems(self, this_parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include NUMBER
                    1
                    2
                    3

                    4
                    5
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert str(result) == ResultsFromFile()
        assert this_parse_mock.method_calls == []
