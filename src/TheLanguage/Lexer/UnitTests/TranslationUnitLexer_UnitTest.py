# ----------------------------------------------------------------------
# |
# |  TranslationUnitLexer_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-27 08:33:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for TranslationUnitLexer.py"""

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
    from ..TranslationUnitLexer import *

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

    from ..Phrases.DSL import (
        CreatePhrase,
        CustomArityPhraseItem,
        DefaultCommentToken,
        OneOrMorePhraseItem,
        OrPhraseItem,
    )


# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock(parse_mock_impl):
    parse_mock_impl.OnPhraseCompleteAsync = CoroutineMock()

    return parse_mock_impl


# ----------------------------------------------------------------------
_upper_token                                = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+[0-9]*)"))
_lower_token                                = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+[0-9]*)"))
_number_token                               = RegexToken("Number", re.compile(r"(?P<value>\d+[a-z]*)"))


# ----------------------------------------------------------------------
class TestSyntaxInvalidError(object):
    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=[
            _upper_token,
            ":",
            NewlineToken(),
            IndentToken(),
            CustomArityPhraseItem.Create(
                OrPhraseItem()
                    | [_upper_token, NewlineToken()]
                    | [_lower_token, NewlineToken()]
                    | [_number_token, NewlineToken()]
                ,
                2,
                4,
            ),
            DedentToken(),
        ],
    )

    _dynamic_phrases                        = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_phrase]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleWord(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
                self._dynamic_phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        SCOPE:
                            one
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [3, 1]

            '{([Upper, Newline+] | [Lower, Newline+] | [Number, Newline+]), 2, 4}' was expected.
            """,
        )

        assert ex.Line == 3
        assert ex.Column == 1

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleWords(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
                self._dynamic_phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        SCOPE:
                            one _two
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [2, 9]

            'Newline+' was expected in '[Lower, Newline+]'.
            """,
        )

        assert ex.Line == 2
        assert ex.Column == 9

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_4thLine1stToken(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
                self._dynamic_phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        SCOPE:
                            one
                            two
                            _invalid
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [4, 1]

            'Dedent' was expected in 'Phrase'.
            """,
        )

        assert ex.Line == 4
        assert ex.Column == 1

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_4thLine2ndToken(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
                self._dynamic_phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        SCOPE:
                            one
                            two
                            three _invalid
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [4, 11]

            'Newline+' was expected in '[Lower, Newline+]'.
            """,
        )

        assert ex.Line == 4
        assert ex.Column == 11

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_4thLine2ndTokenNumber(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
                self._dynamic_phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        SCOPE:
                            one
                            two
                            3 _invalid
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [4, 7]

            'Newline+' was expected in '[Number, Newline+]'.
            """,
        )

        assert ex.Line == 4
        assert ex.Column == 7

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_WayOff1(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
                self._dynamic_phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        nope
                        way_off
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [1, 1]

            # <class 'TheLanguage.Lexer.Components.AST.Node'>
            Children:
              - # <class 'TheLanguage.Lexer.Components.AST.Node'>
                Children:
                  - # <class 'TheLanguage.Lexer.Components.AST.Node'>
                    Children:
                      - # <class 'TheLanguage.Lexer.Components.AST.Node'>
                        Children:
                          - # <class 'TheLanguage.Lexer.Components.AST.Node'>
                            Children: []
                            IterBegin: None
                            IterEnd: None
                            Type: "Upper <class 'TheLanguage.Lexer.Phrases.TokenPhrase.TokenPhrase'>"
                        IterBegin: None
                        IterEnd: None
                        Type: "Phrase <class 'TheLanguage.Lexer.Phrases.SequencePhrase.SequencePhrase'>"
                    IterBegin: None
                    IterEnd: None
                    Type: "(Phrase) <class 'TheLanguage.Lexer.Phrases.OrPhrase.OrPhrase'>"
                IterBegin: None
                IterEnd: None
                Type: "Dynamic Phrases <class 'TheLanguage.Lexer.Phrases.DynamicPhrase.DynamicPhrase'>"
            IterBegin: None
            IterEnd: None
            Type: "<None>"
            """,
        )

        assert ex.Line == 1
        assert ex.Column == 1

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoChildren(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
                self._dynamic_phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        SCOPE:
                            _nope
                        """,
                    ),
                ),
                parse_mock,
            )

        ex = ex.value

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [2, 5]

            '{([Upper, Newline+] | [Lower, Newline+] | [Number, Newline+]), 2, 4}' was expected in 'Phrase'.
            """,
        )

        assert ex.Line == 2
        assert ex.Column == 5


# ----------------------------------------------------------------------
class TestInterestingWhitespace(object):
    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=OneOrMorePhraseItem.Create(
            [_lower_token, NewlineToken()],
        ),
    )

    _dynamic_phrases                        = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_phrase]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InitialComment(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
            self._dynamic_phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    # Comment 1
                    one # Comment 2
                    # Comment 3
                    two # Comment 4
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))


    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InitialNewline(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
            self._dynamic_phrases,
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

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TrailingComment(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
            self._dynamic_phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    one

                    # Comment 1




                    # Comment 2
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_TrailingNewline(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
            self._dynamic_phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    one



                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EmptyContent(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
            self._dynamic_phrases,
            CreateIterator(""),
            parse_mock,
        )

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_AllWhitespace(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
            self._dynamic_phrases,
            CreateIterator(
                textwrap.dedent(
                    """\



                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_CommentIndentation1(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
            self._dynamic_phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    # Comment 0
                    lower

                        # Comment
                    another
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_CommentIndentation2(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
            self._dynamic_phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    # Comment 0
                    lower

                        # Comment 1
                    # Comment 2
                    another
                    """,
                ),
            ),
            parse_mock,
        )

        CompareResultsFromFile(str(result))


# ----------------------------------------------------------------------
class TestSimple(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number Phrase", item=[_number_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_upper_phrase, _lower_phrase, _number_phrase]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchStandard(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result), suffix=".results")
        CompareResultsFromFile(MethodCallsToString(parse_mock), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchReverse(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))
        assert len(parse_mock.method_calls) == 15

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EarlyTermination(self, parse_mock):
        parse_mock.OnPhraseCompleteAsync = CoroutineMock(
            side_effect=[True, False],
        )

        result = await LexAsync(
            DefaultCommentToken,
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

    _phrases                                = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_phrase]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))


# ----------------------------------------------------------------------
class TestNewPhrases(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=_upper_token)
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_upper_phrase,]})
    _new_phrases                            = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_lower_phrase,]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnPhraseCompleteAsync = CoroutineMock(
            side_effect=[self._new_phrases, True, True, True, True, True, True, True, True],
        )

        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
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

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [1, 5]

            'Upper' was expected.
            """,
        )

        assert ex.Line == 1
        assert ex.Column == 5


# ----------------------------------------------------------------------
class TestNewScopedPhrases(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=_upper_token)
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=_lower_token)

    _newline_phrase                         = CreatePhrase(name="Newline Phrase", item=NewlineToken())
    _indent_phrase                          = CreatePhrase(name="Indent Phrase", item=IndentToken())
    _dedent_phrase                          = CreatePhrase(name="Dedent Phrase", item=DedentToken())

    _phrases                                = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_upper_phrase, _newline_phrase, _indent_phrase, _dedent_phrase]})
    _new_phrases                            = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_lower_phrase,]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnPushScopeAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        parse_mock.OnPushScopeAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
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

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [4, 1]

            '(Upper Phrase | Newline Phrase | Indent Phrase | Dedent Phrase)' was expected.
            """,
        )

        assert ex.Line == 4
        assert ex.Column == 1


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

    _phrases                             = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_newline_phrase, _new_scope_phrase] })
    _new_phrases                         = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_upper_phrase, _lower_phrase] })

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnPushScopeAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))


# ----------------------------------------------------------------------
class TestEmbeddedPhrases(object):
    _upper_lower_phrase                     = CreatePhrase(name="Upper Lower Phrase", item=[_upper_token, _lower_token, NewlineToken()])

    _uul_phrase                             = CreatePhrase(name="uul", item=[_upper_token, _upper_lower_phrase])
    _lul_phrase                             = CreatePhrase(name="lul", item=[_lower_token, _upper_lower_phrase])

    _phrases                                = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_uul_phrase, _lul_phrase]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))


# ----------------------------------------------------------------------
class TestVariedLengthMatches(object):
    _upper_phrase                           = CreatePhrase(name="Upper", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower", item=[_lower_token, _lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number", item=[_number_token, _number_token, _number_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_upper_phrase, _lower_phrase, _number_phrase]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))


# ----------------------------------------------------------------------
class TestPreventParentTraversal(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])
    _indent_phrase                          = CreatePhrase(name="Indent Phrase", item=IndentToken())
    _dedent_phrase                          = CreatePhrase(name="Dedent Phrase", item=DedentToken())

    _phrases                                = DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_upper_phrase, _indent_phrase, _dedent_phrase]})

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async  def test_Match(self, parse_mock):
        parse_mock.OnPushScopeAsync = CoroutineMock(
            return_value=DynamicPhrasesInfo(
                {DynamicPhrasesType.Statements: [self._lower_phrase, self._dedent_phrase]},
                AllowParentTraversal=False,
            ),
        )

        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        parse_mock.OnPushScopeAsync = CoroutineMock(
            return_value=DynamicPhrasesInfo(
                {DynamicPhrasesType.Statements: [self._lower_phrase, self._dedent_phrase]},
                AllowParentTraversal=False,
            ),
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            result = await LexAsync(
                DefaultCommentToken,
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

        assert str(ex) == textwrap.dedent(
            """\
            The syntax is not recognized. [6, 1]

            '(Upper Phrase | Indent Phrase | Dedent Phrase)' was expected.
            """,
        )

        assert ex.Line == 6
        assert ex.Column == 1


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_InvalidDynamicTraversalError(parse_mock):
    parse_mock.OnPhraseCompleteAsync = CoroutineMock(
        return_value=DynamicPhrasesInfo(
            {DynamicPhrasesType.Statements: [CreatePhrase(name="Newline", item=NewlineToken()),]},
            AllowParentTraversal=False,
        ),
    )

    with pytest.raises(InvalidDynamicTraversalError) as ex:
        result = await LexAsync(
            DefaultCommentToken,
            DynamicPhrasesInfo(
                {DynamicPhrasesType.Statements: [CreatePhrase(name="Lower", item=_lower_token),]},
            ),
            CreateIterator(
                textwrap.dedent(
                    """\
                    lower
                    """,
                ),
            ),
            parse_mock,
        )

    ex = ex.value

    assert str(ex) == "Dynamic phrases that prohibit parent traversal should never be applied over other dynamic phrases within the same lexical scope; consider making these dynamic phrases the first ones applied in this lexical scope."
    assert ex.Line == 1
    assert ex.Column == 6


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_DynamicExpressions(parse_mock):
    result = await LexAsync(
        DefaultCommentToken,
        DynamicPhrasesInfo(
            {
                DynamicPhrasesType.Statements: [
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

                DynamicPhrasesType.Expressions: [
                    CreatePhrase(
                        name="Expression",
                        item=_number_token,
                    ),
                ],
            },
        ),
        CreateIterator("WORD 1234 lower"),
        parse_mock,
    )

    CompareResultsFromFile(str(result))


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
        {DynamicPhrasesType.Statements: [_lower_include_phrase, _number_include_phrase]},
    )

    _lower_dynamic_phrases                  = DynamicPhrasesInfo(
        {DynamicPhrasesType.Statements: [_lower_phrase,]},
    )

    _number_dynamic_phrases                 = DynamicPhrasesInfo(
        {DynamicPhrasesType.Statements: [_number_phrase,]},
    )

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def this_parse_mock(cls, parse_mock):
        # ----------------------------------------------------------------------
        async def OnPhraseCompleteAsync(
            phrase: Phrase,
            node: AST.Node,
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
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))
        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_LowerAdditionalItem(self, this_parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))
        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Number(self, this_parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))
        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NumberAdditionalItems(self, this_parse_mock):
        result = await LexAsync(
            DefaultCommentToken,
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

        CompareResultsFromFile(str(result))
        assert this_parse_mock.method_calls == []


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_EmptyDynamicPhrasesInfo(parse_mock):
    parse_mock.OnPhraseCompleteAsync = CoroutineMock(
        return_value=DynamicPhrasesInfo({}),
    )

    result = await LexAsync(
        DefaultCommentToken,
        DynamicPhrasesInfo(
            {
                DynamicPhrasesType.Statements: [
                    CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()]),
                ],
            },
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

    CompareResultsFromFile(str(result))
