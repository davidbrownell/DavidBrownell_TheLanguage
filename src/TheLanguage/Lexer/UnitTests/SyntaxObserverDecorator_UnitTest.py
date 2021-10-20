# ----------------------------------------------------------------------
# |
# |  SyntaxObserverDecorator_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-28 09:20:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Syntax.py"""

import os
import textwrap

from unittest.mock import Mock

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

from asynctest import CoroutineMock
from semantic_version import Version as SemVer

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import CompareResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..SyntaxObserverDecorator import *
    from ..TranslationUnitsLexer import LexAsync

    from ..Components.ThreadPool import CreateThreadPool
    from ..Phrases.DSL import DefaultCommentToken


# ----------------------------------------------------------------------
class TestStandard(object):

    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>[0-9]+)"))

    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number Phrase", item=[_number_token, NewlineToken()])

    _syntaxes                               = {
        SemVer("1.0.0") : DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_upper_phrase, _lower_phrase]}),
        SemVer("2.0.0") : DynamicPhrasesInfo({DynamicPhrasesType.Statements: [_upper_phrase, _lower_phrase, _number_phrase]})
    }

    # ----------------------------------------------------------------------
    @classmethod
    def CreateObserver(
        cls,
        content_dict,
        num_threads=None,
    ):
        mock = Mock()
        mock._thread_pool = CreateThreadPool(num_threads)

        mock.LoadContent = lambda fully_qualified_name: content_dict[fully_qualified_name]
        mock.Enqueue = mock._thread_pool.EnqueueAsync

        mock.GetParentStatementNode = Mock(return_value=None)
        mock.OnPushScopeAsync = CoroutineMock()
        mock.OnPopScopeAsync = CoroutineMock()
        mock.OnPhraseCompleteAsync = CoroutineMock()

        return SyntaxObserverDecorator(
            mock,
            cls._syntaxes,
            Configurations.Debug,
            "TheTarget",
        )

    # ----------------------------------------------------------------------
    def test_Properties(self):
        observer = self.CreateObserver({})

        assert observer.DefaultGrammarVersion == SemVer("2.0.0")

        assert len(observer.Grammars) == 2

        # The syntax statements should have been added to each
        assert len(observer.Grammars[SemVer("1.0.0")].Phrases[DynamicPhrasesType.Statements]) == 4
        assert len(observer.Grammars[SemVer("2.0.0")].Phrases[DynamicPhrasesType.Statements]) == 5

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Default(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    UPPER
                    lower
                    1234
                    """,
                ),
            },
        )

        result = await LexAsync(
            DefaultCommentToken,
            ["one"],
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
        )

        assert len(result) == 1
        assert "one" in result
        result = result["one"]

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_V1_NoError(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    AUPPER
                    alower
                    1234

                    __with __syntax=1.0:
                        BUPPER
                        blower

                    __with __syntax=1.0.0:
                        clower

                    456789
                    """,
                ),
            },
        )

        result = await LexAsync(
            DefaultCommentToken,
            ["one"],
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
        )

        assert len(result) == 1
        assert "one" in result
        result = result["one"]

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_V1_NoError_TrailingComments(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    AUPPER
                    alower
                    1234

                    __with __syntax=1.0: # This should not be a problem
                        BUPPER
                        blower

                    __with __syntax=1.0.0:
                        clower

                    456789
                    """,
                ),
            },
        )

        result = await LexAsync(
            DefaultCommentToken,
            ["one"],
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
        )

        assert len(result) == 1
        result = result["one"]

        CompareResultsFromFile(str(result))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_V1_Error(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    AUPPER
                    alower
                    1234

                    __with __syntax=1.0:
                        BUPPER
                        blower
                        1235
                    """,
                ),
            },
        )

        result = await LexAsync(
            DefaultCommentToken,
            ["one"],
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
        )

        assert len(result) == 1
        result = result[0]

        assert str(result) == textwrap.dedent(
            """\
            The syntax is not recognized. [8, 1]

            'Grammar-Specific Statements' were evaluated but not matched; therefore 'Dedent' was expected in 'Set Syntax Statement'.
            """,
        )

        assert result.FullyQualifiedName == "one"
        assert result.Line == 8
        assert result.Column == 1

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InvalidVersion1(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    __with __syntax=4.5.6:
                        UPPER
                    """,
                ),
            },
        )

        result = await LexAsync(
            DefaultCommentToken,
            ["one"],
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
        )

        assert len(result) == 1
        result = result[0]

        assert str(result) == "The syntax version '4.5.6' is not recognized."
        assert result.InvalidVersion == SemVer.coerce("4.5.6")
        assert result.FullyQualifiedName == "one"
        assert result.Line == 1
        assert result.Column == 17

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InvalidVersion2(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    __with __syntax = 4.5:
                        UPPER
                    """,
                ),
            },
        )

        result = await LexAsync(
            DefaultCommentToken,
            ["one"],
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
        )

        assert len(result) == 1
        result = result[0]

        assert str(result) == "The syntax version '4.5.0' is not recognized."
        assert result.InvalidVersion == SemVer.coerce("4.5.0")
        assert result.FullyQualifiedName == "one"
        assert result.Line == 1
        assert result.Column == 19

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InvalidVersionFormat(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    __with __syntax = this_is_not_a_valid_version:
                        UPPER
                    """,
                ),
            },
        )

        result = await LexAsync(
            DefaultCommentToken,
            ["one"],
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
        )

        assert len(result) == 1
        result = result[0]

        assert str(result) == "The syntax version 'this_is_not_a_valid_version' is not a valid version."
        assert result.InvalidVersion == "this_is_not_a_valid_version"
        assert result.FullyQualifiedName == "one"
        assert result.Line == 1
        assert result.Column == 19

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_IfStatements(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    __if __syntax == 1.2.3:
                        fooa

                    __if not __syntax == 4.0:
                        foob

                    __if (__syntax < 1.0 and __syntax > 2.0):
                        fooc

                    __if (__syntax != 2.0 and (__syntax != 2.0 or __syntax != 3.0)):
                        food
                        fooe
                    """,
                ),
            },
        )

        result = await LexAsync(
            DefaultCommentToken,
            ["one"],
            observer.Grammars[observer.DefaultGrammarVersion],
            observer,
        )

        assert len(result) == 1
        result = result["one"]

        CompareResultsFromFile(str(result))



# TODO: Add tests for more complicated comparison scenarios
