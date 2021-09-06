# ----------------------------------------------------------------------
# |
# |  Phrase_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-24 07:26:11
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
        @Interface.override
        async def _ParseAsyncImpl(self, *args, **kwargs):
            return self.parse_mock(*args, **kwargs)

    # ----------------------------------------------------------------------

    return ThePhrase()

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
        @Interface.override
        def _PopulateRecursiveImpl(
            self,
            new_phrase: Phrase,
        ) -> bool:
            # Nothing to do here
            return False

        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        async def _ParseAsyncImpl(*args, **kwargs):
            pass

    # ----------------------------------------------------------------------
    class MyParseResultData(Phrase.ParseResultData):
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
    def test_ParseResultEmptyData(self, iterator):
        assert str(Phrase.ParseResult(True, iterator, iterator, None)) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data: None
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultAdvancedIterator(self, iterator):
        iterator.Advance(5)

        assert str(Phrase.ParseResult(True, iterator, iterator, None)) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data: None
            IterBegin: "[1, 6] (5)"
            IterEnd: "[1, 6] (5)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultWithMyParseResultData(self, iterator):
        assert str(
            Phrase.ParseResult(False, iterator, iterator, self.MyParseResultData()),
        ) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data: # <class 'TheLanguage.Parser.Components.UnitTests.Phrase_UnitTest.TestStandard.MyParseResultData'>
              {}
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: False
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultWithStandardParseResultData(self, iterator):
        assert str(Phrase.ParseResult(
            True,
            iterator,
            iterator,
            Phrase.StandardParseResultData(
                CreatePhrase(20),
                self.MyParseResultData(),
                ["id1"],
            ),
        )) == textwrap.dedent(
            """\
            # <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data: # <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
              Data: # <class 'TheLanguage.Parser.Components.UnitTests.Phrase_UnitTest.TestStandard.MyParseResultData'>
                {}
              Phrase: "The Phrase"
            IterBegin: "[1, 1] (0)"
            IterEnd: "[1, 1] (0)"
            Success: True
            """,
        )

    # ----------------------------------------------------------------------
    def test_StandardParseResultDataEnumWithNone(self):
        phrase = CreatePhrase(20)

        data = Phrase.StandardParseResultData(
            phrase,
            None,
            None,
        )


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_Parse(iterator, parse_mock):
    result = await CreatePhrase(1).ParseAsync(("root", ), iterator, parse_mock)
    assert result.Success == 1

    assert parse_mock.OnIndent.call_count == 0
    assert parse_mock.OnDedent.call_count == 0
    assert parse_mock.OnInternalPhrase.call_count == 0
