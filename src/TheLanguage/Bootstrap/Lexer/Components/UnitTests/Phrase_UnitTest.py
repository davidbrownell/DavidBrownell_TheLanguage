# ----------------------------------------------------------------------
# |
# |  Phrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 18:09:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for Phrase.py"""

import os
import textwrap

from unittest.mock import Mock

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import CreateIterator, parse_mock

    from ..Phrase import *

    from ..Normalize import Normalize
    from ..NormalizedIterator import NormalizedIterator


# ----------------------------------------------------------------------
def CreatePhrase(result):

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ResultObject(object):
        Success: Any

    # ----------------------------------------------------------------------

    result_obj = ResultObject(result)

    # ----------------------------------------------------------------------
    class ThePhrase(Phrase):
        # ----------------------------------------------------------------------
        def __init__(self):
            super(ThePhrase, self).__init__("The Phrase")

            self.parse_mock = Mock(
                return_value=result_obj,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def LexAsync(self, *args, **kwargs):
            return self.parse_mock(*args, **kwargs)

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        @Interface.override
        def _PopulateRecursiveImpl(
            self,
            new_phrase: Phrase,
        ) -> bool:
            # Nothing to do here
            return True

    # ----------------------------------------------------------------------

    phrase = ThePhrase()

    phrase.PopulateRecursive(None, phrase)
    return phrase


# ----------------------------------------------------------------------
@pytest.fixture
def iterator(
    value="This is the content",
):
    return NormalizedIterator.FromNormalizedContent(Normalize(value))


# ----------------------------------------------------------------------
class TestStandard(object):
    # ----------------------------------------------------------------------
    class MyPhrase(Phrase):
        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        async def LexAsync(*args, **kwargs):
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
    class MyLexResultData(Phrase.LexResultData):
        pass

    # ----------------------------------------------------------------------
    def test_Properties(self):
        assert self.MyPhrase("The phrase name").Name == "The phrase name"

    # ----------------------------------------------------------------------
    def test_PropertyErrors(self):
        with pytest.raises(AssertionError):
            self.MyPhrase("")

    # ----------------------------------------------------------------------
    def test_Equality(self):
        hello = self.MyPhrase("hello")
        goodbye = self.MyPhrase("goodbye")

        assert hello == hello
        assert goodbye != hello
        assert self.MyPhrase("hello") != self.MyPhrase("hello")

    # ----------------------------------------------------------------------
    def test_LexResultEmptyData(self, iterator):
        assert str(Phrase.LexResult(True, iterator, iterator, None)) == textwrap.dedent(
            """\
            # <class 'Bootstrap.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: None
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    def test_LexResultAdvancedIterator(self, iterator):
        iterator.Advance(5)

        assert str(Phrase.LexResult(True, iterator, iterator, None)) == textwrap.dedent(
            """\
            # <class 'Bootstrap.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: None
            IterBegin: "[1, 6] (5)"
            IterEnd: "[1, 6] (5)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    def test_LexResultWithMyLexResultData(self, iterator):
        assert str(
            Phrase.LexResult(False, iterator, iterator, self.MyLexResultData()),
        ) == textwrap.dedent(
            """\
            # <class 'Bootstrap.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'Bootstrap.Lexer.Components.UnitTests.Phrase_UnitTest.TestStandard.MyLexResultData'>
              {}
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: False
            """,
        )

    # ----------------------------------------------------------------------
    def test_LexResultWithStandardLexResultData(self, iterator):
        assert str(Phrase.LexResult(
            True,
            iterator,
            iterator,
            Phrase.StandardLexResultData(
                CreatePhrase(20),
                self.MyLexResultData(),
                ["id1"],
            ),
        )) == textwrap.dedent(
            """\
            # <class 'Bootstrap.Lexer.Components.Phrase.Phrase.LexResult'>
            Data: # <class 'Bootstrap.Lexer.Components.Phrase.Phrase.StandardLexResultData'>
              Data: # <class 'Bootstrap.Lexer.Components.UnitTests.Phrase_UnitTest.TestStandard.MyLexResultData'>
                {}
              Phrase: "The Phrase"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    def test_StandardLexResultDataEnumWithNone(self):
        phrase = CreatePhrase(20)

        data = Phrase.StandardLexResultData(
            phrase,
            None,
            None,
        )


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_Lex(iterator, parse_mock):
    result = await CreatePhrase(1).LexAsync(("root", ), iterator, parse_mock)
    assert result.Success == 1

    assert parse_mock.OnIndent.call_count == 0
    assert parse_mock.OnDedent.call_count == 0
    assert parse_mock.OnInternalPhrase.call_count == 0
