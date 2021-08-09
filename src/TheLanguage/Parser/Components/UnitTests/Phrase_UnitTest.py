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
import re
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
    class ThePhrase(Phrase):
        # ----------------------------------------------------------------------
        def __init__(self):
            super(ThePhrase, self).__init__("The Phrase")

            self.parse_mock = Mock(
                return_value=result,
            )

        # ----------------------------------------------------------------------
        @Interface.override
        async def ParseAsync(self, *args, **kwargs):
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

    return ThePhrase()

# ----------------------------------------------------------------------
@pytest.fixture
def iterator(
    value="This is the content",
):
    return NormalizedIterator(Normalize(value))

# ----------------------------------------------------------------------
class TestStandard(object):
    # ----------------------------------------------------------------------
    class MyPhrase(Phrase):
        # ----------------------------------------------------------------------
        @staticmethod
        @Interface.override
        async def ParseAsync(*args, **kwargs):
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
            return False

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
        assert str(Phrase.ParseResult(True, iterator, None)) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : None
            Iter    : [1, 1] (0)
            Success : True
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultAdvancedIterator(self, iterator):
        iterator.Advance(5)

        assert str(Phrase.ParseResult(True, iterator, None)) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : None
            Iter    : [1, 6] (5)
            Success : True
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultWithMyParseResultData(self, iterator):
        assert str(Phrase.ParseResult(False, iterator, self.MyParseResultData())) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.UnitTests.Phrase_UnitTest.TestStandard.MyParseResultData'>
                      -- empty dict --
            Iter    : [1, 1] (0)
            Success : False
            """,
        )

    # ----------------------------------------------------------------------
    def test_ParseResultWithStandardParseResultData(self, iterator):
        assert Phrase.ParseResult(
            True,
            iterator,
            Phrase.StandardParseResultData(
                CreatePhrase(20),
                self.MyParseResultData(),
                ["id1"],
            ),
        ).ToString() == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.Phrase.Phrase.ParseResult'>
            Data    : <class 'TheLanguage.Parser.Components.Phrase.Phrase.StandardParseResultData'>
                      Data     : <class 'TheLanguage.Parser.Components.UnitTests.Phrase_UnitTest.TestStandard.MyParseResultData'>
                                 -- empty dict --
                      Phrase   : <class 'TheLanguage.Parser.Components.UnitTests.Phrase_UnitTest.CreatePhrase.<locals>.ThePhrase'>
                                 Name : The Phrase
                      UniqueId : 0)   id1
            Iter    : [1, 1] (0)
            Success : True
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
# TODO: Restore this test
# class TestMultipleParseResultData(object):
#     _token                                  = RegexToken("My Word Token", re.compile(r"(?P<value>[a-zA-Z0-9]+)"))
#     _phrase                                 = TokenPhrase(_token)
#     _iterator                               = CreateIterator("one two")
#
#     _data                                   = Phrase.MultipleStandardParseResultData(
#         [
#             Phrase.StandardParseResultData(
#                 _phrase,
#                 Phrase.TokenParseResultData(
#                     _token,
#                     None,
#                     Token.RegexMatch(_token.Regex.match("one")),
#                     _iterator,
#                     _iterator,
#                     False,
#                 ),
#                 ["id1"],
#             ),
#             Phrase.StandardParseResultData(
#                 _phrase,
#                 Phrase.TokenParseResultData(
#                     _token,
#                     None,
#                     Token.RegexMatch(_token.Regex.match("two")),
#                     _iterator,
#                     _iterator,
#                     False,
#                 ),
#                 ["id2"],
#             ),
#         ],
#         True,
#     )
#
#     # ----------------------------------------------------------------------
#     def test_String(self):
#         assert str(self._data) == textwrap.dedent(
#             """\
#             My Word Token
#                 My Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 1]
#             My Word Token
#                 My Word Token <<Regex: <_sre.SRE_Match object; span=(0, 3), match='two'>>> ws:None [1, 1 -> 1, 1]
#             """,
#         )
#
#     # ----------------------------------------------------------------------
#     def test_Enum(self):
#         assert list(self._data.Enum()) == [
#             (self._phrase, self._data.DataItems[0].Data, self._data.DataItems[0].UniqueId),
#             (self._phrase, self._data.DataItems[1].Data, self._data.DataItems[1].UniqueId),
#         ]

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_Parse(iterator, parse_mock):
    result = await CreatePhrase(1).ParseAsync(iterator, parse_mock)
    assert result == 1

    assert parse_mock.OnIndent.call_count == 0
    assert parse_mock.OnDedent.call_count == 0
    assert parse_mock.OnInternalPhrase.call_count == 0
