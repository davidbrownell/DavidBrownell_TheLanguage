# ----------------------------------------------------------------------
# |
# |  LeftRecursiveSequencePhraseWrapper_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-27 13:39:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for LeftRecursiveSequencePhraseWrapper"""

import os
import re

from typing import cast

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
    from ..LeftRecursiveSequencePhraseWrapper import *

    from ...Components.Token import RegexToken

    from ...Components.UnitTests import (
        CoroutineMock,
        CreateIterator,
        parse_mock as parse_mock_impl,
        MethodCallsToString,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _standard_phrases                       = [
        CreatePhrase(RegexToken("Lower", re.compile(r"(?P<value>[a-z_]+[0-9]*)"))),
        CreatePhrase(RegexToken("Upper", re.compile(r"(?P<value>[A-Z_]+[0-9]*)"))),
    ]

    _left_recursive_phrases                 = [
        CreatePhrase(name="Add", item=[DynamicPhrasesType.Statements, "+", DynamicPhrasesType.Statements]),
        CreatePhrase(name="Sub", item=[DynamicPhrasesType.Statements, "-", DynamicPhrasesType.Statements]),
        CreatePhrase(name="Mul", item=[DynamicPhrasesType.Statements, "*", DynamicPhrasesType.Statements]),
        CreatePhrase(name="Div", item=[DynamicPhrasesType.Statements, "/", DynamicPhrasesType.Statements]),
        CreatePhrase(name="Ter", item=[DynamicPhrasesType.Statements, "if", DynamicPhrasesType.Statements, "else", DynamicPhrasesType.Statements]),
        CreatePhrase(name="Index", item=[DynamicPhrasesType.Statements, "[", DynamicPhrasesType.Statements, "]"]),
    ]

    _left_recursive_phrase                  = LeftRecursiveSequencePhraseWrapper(
        DynamicPhrasesType.Statements,
        _standard_phrases,
        cast(List[SequencePhrase], _left_recursive_phrases),
        prefix_name="Phrases",
    )

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def parse_mock(cls, parse_mock_impl):
        # ----------------------------------------------------------------------
        def GetDynamicPhrases(*args, **kwargs):
            return "Phrases", cls._standard_phrases + [cls._left_recursive_phrase]

        # ----------------------------------------------------------------------

        parse_mock_impl.GetDynamicPhrases = GetDynamicPhrases

        return parse_mock_impl

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        # No match, as we are explicitly asking for a left-recursive match
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("this_will_not_match"),
                    parse_mock,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Simple(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("one + TWO"),
                    parse_mock,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_3Items(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("one + TWO - three"),
                    parse_mock,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_4Items(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("one + TWO - three * FOUR"),
                    parse_mock,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_1Index(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("var[a]"),
                    parse_mock,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_2Indexes(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("var[a][b]"),
                    parse_mock,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_ManyIndexes(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("var[a][b][c][d][e][f][g]"),
                    parse_mock,
                ),
            ),
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Complicated1(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("one + true if CONDITION else false - three[a][b][c][d] * FOUR"),
                    parse_mock,
                    single_threaded=True,
                ),
            ),
            suffix=".results",
        )

        CompareResultsFromFile(MethodCallsToString(parse_mock), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Complicated2(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("one + var[a][b][c] + three + four if CONDITION else five"),
                    parse_mock,
                    single_threaded=True,
                ),
            ),
            suffix=".results",
        )

        CompareResultsFromFile(MethodCallsToString(parse_mock), suffix=".events", file_ext=".txt")

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Complicated3(self, parse_mock):
        CompareResultsFromFile(
            str(
                await self._left_recursive_phrase.ParseAsync(
                    ("root", ),
                    CreateIterator("TRUE if var[a][one if CONDITION else two] else FALSE"),
                    parse_mock,
                    single_threaded=True,
                ),
            ),
            suffix=".results",
        )

        CompareResultsFromFile(MethodCallsToString(parse_mock), suffix=".events", file_ext=".txt")
