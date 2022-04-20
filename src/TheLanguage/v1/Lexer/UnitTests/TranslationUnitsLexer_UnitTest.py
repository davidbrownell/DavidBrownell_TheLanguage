# ----------------------------------------------------------------------
# |
# |  TranslationUnitsLexer_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-02 11:42:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for TranslationUnitsLexer.py"""

import os
import re
import textwrap

from typing import Dict, Optional
from unittest.mock import Mock

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import CompareResultsFromFile
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
with InitRelativeImports():
    from ..TranslationUnitsLexer import *

    from ..Components.AST import Node
    from ..Components.ThreadPool import CreateThreadPool

    from ..Components.Tokens import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )

    from ..Components.UnitTests import MethodCallsToString

    from ..Phrases.DSL import (
        CreatePhrase,
        DefaultCommentToken,
        DynamicPhrasesType,
        ExtractSequence,
        ExtractToken,
    )


# ----------------------------------------------------------------------
class TestStandard(object):
    _content_dict                           = {
        "upper" : textwrap.dedent(
            """\
            FOUR
            Five
            SIX
            """,
        ),
        "lower" : textwrap.dedent(
            """\
            four
            five
            six
            """,
        ),
        "number" : textwrap.dedent(
            """\
            4
            5
            6
            """,
        ),
    }

    _include_token                          = RegexToken("Include Token", re.compile(r"(?P<value>include)"))
    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>[0-9]+)"))

    _include_phrase                         = CreatePhrase(name="Include", item=[_include_token, _lower_token, NewlineToken()])
    _upper_phrase                           = CreatePhrase(name="Upper", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower", item=[_lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number", item=[_number_token, NewlineToken()])

    _new_scope_phrase                       = CreatePhrase(
        name="New Scope",
        item=[
            _upper_token,
            RegexToken("Colon Token", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DedentToken(),
        ],
    )

    _dynamic_number_phrase                  = CreatePhrase(
        name="Dynamic Number",
        item=[
            _number_token,
            _number_token,
            _number_token,
            NewlineToken(),
        ],
    )

    _phrases                                = DynamicPhrasesInfo(
        {
            DynamicPhrasesType.Statements: [_include_phrase, _upper_phrase, _lower_phrase, _number_phrase, _new_scope_phrase],
        },
    )

    _or_phrase_name                         = "{Include, Upper, Lower, Number, New Scope}"
    _dynamic_or_phrase_name                 = "{Include, Upper, Lower, Number, New Scope} / {Dynamic Number}"

    _dynamic_phrases_name                   = "Dynamic Phrases"

    # ----------------------------------------------------------------------
    @classmethod
    def CreateObserver(
        cls,
        content_dict: Dict[str, str],
        num_threads: Optional[int]=None,
    ):
        for k, v in cls._content_dict.items():
            if k not in content_dict:
                content_dict[k] = v

        pool = CreateThreadPool()

        # ----------------------------------------------------------------------
        class MyObserver(Observer):
            # ----------------------------------------------------------------------
            def __init__(self):
                self.on_phrase_complete_mock        = Mock(
                    return_value=True,
                )

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def LoadContent(
                fully_qualified_name: str,
            ) -> str:
                assert fully_qualified_name in content_dict
                return content_dict[fully_qualified_name]

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def ExtractDynamicPhrases(
                fully_qualified_name: str,
                node: Node,
            ) -> DynamicPhrasesInfo:
                if fully_qualified_name == "number":
                    return DynamicPhrasesInfo(
                        {
                            DynamicPhrasesType.Statements: [cls._dynamic_number_phrase],
                        },
                    )

                return DynamicPhrasesInfo({})

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def GetParentStatementNode(
                node: Node,
            ) -> Optional[None]:
                return None

            # ----------------------------------------------------------------------
            @Interface.override
            def Enqueue(
                self,
                func_infos: List[EnqueueFuncInfoType],
            ) -> EnqueueReturnType:
                return pool.Enqueue(func_infos)

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def OnPushScope(
                fully_qualified_name: str,
                iter_range: Phrase.NormalizedIteratorRange,
                data: Phrase.LexResultData,
            ) -> Optional[DynamicPhrasesInfo]:
                return None

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def OnPopScope(
                fully_qualified_name: str,
                iter_range: Phrase.NormalizedIteratorRange,
                data: Phrase.LexResultData,
            ) -> None:
                return None

            # ----------------------------------------------------------------------
            @Interface.override
            def OnPhraseComplete(
                self,
                fully_qualified_name: str,
                phrase: Phrase,
                iter_range: Phrase.NormalizedIteratorRange,
                node: Node,
            ) -> Union[
                bool,                                   # True to continue processing, False to terminate
                DynamicPhrasesInfo,                     # DynamicPhrasesInfo generated by the phrase
                "Observer.ImportInfo",                  # Import information generated by the phrase
            ]:
                if node.type == cls._include_phrase:
                    children = ExtractSequence(node)
                    assert len(children) == 3

                    value = cast(str, ExtractToken(children[1]))

                    return Observer.ImportInfo(value, value if value in cls._content_dict else None)

                return self.on_phrase_complete_mock(iter_range, node)

        # ----------------------------------------------------------------------

        return MyObserver()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_NoInclude(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    3
                    """,
                ),
            },
            num_threads=5,
        )

        results = Lex(
            DefaultCommentToken,
            ["one"],
            self._phrases,
            observer,
            single_threaded=True,
        )

        assert len(results) == 1
        assert "one" in results
        results = results["one"]

        CompareResultsFromFile(results.ToYamlString(), suffix=".results")
        CompareResultsFromFile(
            MethodCallsToString(
                observer.on_phrase_complete_mock,
                attribute_name="call_args_list",
            ),
            suffix=".events",
            file_ext=".txt",
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_SingleInclude(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include number
                    3
                    """,
                ),
            },
        )

        all_results = Lex(
            DefaultCommentToken,
            ["one"],
            self._phrases,
            observer,
            single_threaded=True,
        )

        assert len(all_results) == 2
        assert "one" in all_results
        assert "number" in all_results

        one_results = all_results["one"]
        CompareResultsFromFile(str(one_results), suffix=".one_results")

        number_results = all_results["number"]
        CompareResultsFromFile(str(number_results), suffix=".number_results")

        CompareResultsFromFile(
            MethodCallsToString(
                observer.on_phrase_complete_mock,
                attribute_name="call_args_list",
            ),
            suffix=".events",
            file_ext=".txt",
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_DoubleInclude(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include number
                    3
                    include number
                    4
                    """,
                ),
            },
            num_threads=10,
        )

        all_results = Lex(
            DefaultCommentToken,
            ["one"],
            self._phrases,
            observer,
            single_threaded=True,
        )

        assert len(all_results) == 2
        assert "one" in all_results
        assert "number" in all_results

        one_results = all_results["one"]
        CompareResultsFromFile(str(one_results), suffix=".results")

        CompareResultsFromFile(
            MethodCallsToString(
                observer.on_phrase_complete_mock,
                attribute_name="call_args_list",
            ),
            suffix=".events",
            file_ext=".txt",
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_InvalidInclude(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include invalid
                    3
                    """,
                ),
            },
            num_threads=10,
        )

        results = Lex(
            DefaultCommentToken,
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 1
        results = results[0]

        assert str(results) == "'invalid' could not be found"
        assert results.location.line == 3
        assert results.location.column == 1
        assert results.source_name == "invalid"
        assert results.fully_qualified_name == "one"

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_MultipleFileSingleImport(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    one
                    TWO
                    include number
                    3
                    """,
                ),
                "two" : textwrap.dedent(
                    """\
                    aaa
                    BBBB
                    include number
                    cccccc
                    """,
                ),
            },
            num_threads=10,
        )

        results = Lex(
            DefaultCommentToken,
            ["one", "two"],
            self._phrases,
            observer,
        )

        assert len(results) == 3
        assert "one" in results
        assert "two" in results
        assert "number" in results

        one_results = results["one"]
        CompareResultsFromFile(str(one_results), suffix=".one_results")

        two_results = results["two"]
        CompareResultsFromFile(str(two_results), suffix=".two_results")

        number_results = results["number"]
        CompareResultsFromFile(str(number_results), suffix=".number_results")

        assert len(observer.on_phrase_complete_mock.call_args_list) == 60

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_InsertedPhrasesError(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    1 2 3
                    """,
                ),
            },
        )

        results = Lex(
            DefaultCommentToken,
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 1
        results = results[0]

        # assert str(results) == "The syntax is not recognized [Ln 1, Col 3]: 'Newline+' was expected in 'Number'."
        assert str(results) == "The syntax is not recognized [Ln 1, Col 3]: Error context is not available at this time"
        assert results.location.line == 1
        assert results.location.column == 3
        assert results.fully_qualified_name == "one"

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_InsertedPhrasesSuccess(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    include number
                    1 2 3
                    """,
                ),
            },
        )

        results = Lex(
            DefaultCommentToken,
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 2
        assert "one" in results
        assert "number" in results

        one_results = results["one"]
        CompareResultsFromFile(str(one_results))

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_InsertedScopedPhrasesError(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    NEWSCOPE:
                        include number
                        4 5 6
                    7 8 9
                    """,
                ),
            },
            num_threads=10,
        )

        results = Lex(
            DefaultCommentToken,
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 1
        results = results[0]

        assert results.location.line == 4
        assert results.location.column == 3
        # assert str(results) == "The syntax is not recognized [Ln 4, Col 3]: 'Newline+' was expected in 'Number'."
        assert str(results) == "The syntax is not recognized [Ln 4, Col 3]: Error context is not available at this time"

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    def test_InsertedScopedPhrasesSuccess(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    NEWSCOPE:
                        include number
                        1 2 3
                    """,
                ),
            },
        )

        results = Lex(
            DefaultCommentToken,
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 2
        assert "one" in results
        assert "number" in results

        one_results = results["one"]
        CompareResultsFromFile(str(one_results))

# ----------------------------------------------------------------------
def test_NodeStrNoChildren():
    node = Node(CreatePhrase(name="Phrase", item=NewlineToken()))

    CompareResultsFromFile(str(node))

# TODO: Circular dependencies
