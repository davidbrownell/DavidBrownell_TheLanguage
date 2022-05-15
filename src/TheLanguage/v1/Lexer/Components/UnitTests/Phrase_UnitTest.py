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
        success: Any

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
        def Lex(self, *args, **kwargs):
            return self.parse_mock(*args, **kwargs)

        # ----------------------------------------------------------------------
        @Interface.override
        def PrettyPrint(self, *args, **kwargs):
            pass

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
        async def Lex(*args, **kwargs):
            pass

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
    class MyLexResultData(Phrase.LexResultData):
        pass

    # ----------------------------------------------------------------------
    def test_Properties(self):
        assert self.MyPhrase("The phrase name").name == "The phrase name"

    # ----------------------------------------------------------------------
    # def test_PropertyErrors(self):
    #     with pytest.raises(AssertionError):
    #         self.MyPhrase("")

    # ----------------------------------------------------------------------
    def test_Equality(self):
        hello = self.MyPhrase("hello")
        goodbye = self.MyPhrase("goodbye")

        assert hello == hello
        assert goodbye != hello
        # assert self.MyPhrase("hello") != self.MyPhrase("hello")

    # # ----------------------------------------------------------------------
    # def test_LexResultEmptyData(self, iterator):
    #     assert str(Phrase.LexResult(True, Phrase.NormalizedIteratorRange(iterator, iterator), None)) == textwrap.dedent(
    #         """\
    #         # <class 'v1.Lexer.Components.Phrase.Phrase.LexResult'>
    #         data: null
    #    #    #         success: true
    #         """,
    #     )

    # ----------------------------------------------------------------------
    def test_LexResultWithMyLexResultData(self, iterator):
        result = Phrase.LexResult(
            False,
            Phrase.NormalizedIteratorRange(iterator, iterator),
            Phrase.LexResultData(None, ("root", ), None, None),
        )

        assert result.success is False
        assert result.iter_range.begin.offset == 0
        assert result.iter_range.end.offset == 0

    # ----------------------------------------------------------------------
    def test_StandardLexResultDataEnumWithNone(self):
        phrase = CreatePhrase(20)

        data = Phrase.LexResultData(
            phrase,
            ("root", ),
            None,
            None,
        )


# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_Lex(iterator, parse_mock):
    result = CreatePhrase(1).Lex(("root", ), iterator, parse_mock)
    assert result.success == 1

    assert parse_mock.OnInternalPhrase.call_count == 0
