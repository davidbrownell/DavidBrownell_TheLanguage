# ----------------------------------------------------------------------
# |
# |  TranslationUnitsParser_UnitTest.py
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
"""Unit tests for TranslationUnitsParser.py"""

import os
import re
import textwrap

from contextlib import contextmanager
from typing import Dict, Optional
from unittest.mock import Mock

import pytest

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
with InitRelativeImports():
    from ..Components.AST import Node
    from ..Components.ThreadPool import CreateThreadPool

    from ..Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )

    from ..Components.UnitTests import MethodCallsToString

    from ..TranslationUnitsParser import *

    from ..Phrases.DSL import (
        CreatePhrase,
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
        [],
        [],
        [_include_phrase, _upper_phrase, _lower_phrase, _number_phrase, _new_scope_phrase],
        [],
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
            @Interface.override
            def Enqueue(
                self,
                func_infos: List[Phrase.EnqueueAsyncItemType],
            ) -> Awaitable[Any]:
                return pool.EnqueueAsync(func_infos)

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def ExtractDynamicPhrases(
                fully_qualified_name: str,
                node: RootNode,
            ) -> DynamicPhrasesInfo:
                if fully_qualified_name == "number":
                    return DynamicPhrasesInfo([], [], [cls._dynamic_number_phrase], [])

                return DynamicPhrasesInfo([], [], [], [])

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            async def OnIndentAsync(
                fully_qualified_name: str,
                data_stack: List[Phrase.StandardParseResultData],
                iter_before: NormalizedIterator,
                iter_after: NormalizedIterator,
            ) -> Optional[DynamicPhrasesInfo]:
                return None

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            async def OnDedentAsync(
                fully_qualified_name: str,
                data_stack: List[Phrase.StandardParseResultData],
                iter_before: NormalizedIterator,
                iter_after: NormalizedIterator,
            ) -> None:
                return None

            # ----------------------------------------------------------------------
            @Interface.override
            async def OnPhraseCompleteAsync(
                self,
                fully_qualified_name: str,
                phrase: Phrase,
                node: Node,
                iter_before: NormalizedIterator,
                iter_after: NormalizedIterator,
            ) -> Union[
                bool,                                   # True to continue processing, False to terminate
                DynamicPhrasesInfo,                     # DynamicPhrasesInfo generated by the phrase
                "Observer.ImportInfo",                  # Import information generated by the phrase
            ]:
                if node.Type == cls._include_phrase:
                    children = ExtractSequence(node)
                    assert len(children) == 3

                    value = cast(str, ExtractToken(children[1]))  # type: ignore

                    return Observer.ImportInfo(value, value if value in cls._content_dict else None)

                return self.on_phrase_complete_mock(node, iter_before, iter_after)

        # ----------------------------------------------------------------------

        return MyObserver()

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoInclude(self):
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

        results = await ParseAsync(
            ["one"],
            self._phrases,
            observer,
            single_threaded=True,
        )

        assert len(results) == 1
        assert "one" in results
        results = results["one"]

        assert results.ToString() == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (4)
                                                                                    IterBefore : [1, 4] (3)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 4
                                                                                                 Start : 3
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (4)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 4] (7)
                                                                                    IterBefore : [2, 1] (4)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (8)
                                                                                    IterBefore : [2, 4] (7)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 8
                                                                                                 Start : 7
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (8)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 2] (9)
                                                                                    IterBefore : [3, 1] (8)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 9), match='3'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (10)
                                                                                    IterBefore : [3, 2] (9)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 10
                                                                                                 Start : 9
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (10)
                                                                  IterBefore : [3, 1] (8)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (10)
                                                IterBefore : [3, 1] (8)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (10)
                              IterBefore : [3, 1] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (10)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert MethodCallsToString(
            observer.on_phrase_complete_mock,
            attribute_name="call_args_list",
        ) == textwrap.dedent(
            """\
            0) 0, 3
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [1, 4] (3)
                IterBefore : [1, 1] (0)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                Whitespace : None
            1) 3, 4
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 4] (3)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 4
                             Start : 3
                Whitespace : None
            2) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [1, 4] (3)
                                  IterBefore : [1, 1] (0)
                                  Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 4] (3)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 4
                                               Start : 3
                                  Whitespace : None
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            3) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [1, 4] (3)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 1] (4)
                                                    IterBefore : [1, 4] (3)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 4
                                                                 Start : 3
                                                    Whitespace : None
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 1] (0)
                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            4) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [1, 4] (3)
                                                                      IterBefore : [1, 1] (0)
                                                                      Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 1] (4)
                                                                      IterBefore : [1, 4] (3)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 4
                                                                                   Start : 3
                                                                      Whitespace : None
                                                    IterAfter  : [2, 1] (4)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 1] (0)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            5) 4, 7
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 4] (7)
                IterBefore : [2, 1] (4)
                Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                Whitespace : None
            6) 7, 8
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 4] (7)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 8
                             Start : 7
                Whitespace : None
            7) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 4] (7)
                                  IterBefore : [2, 1] (4)
                                  Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 4] (7)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 8
                                               Start : 7
                                  Whitespace : None
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            8) 4, 7
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 4] (7)
                IterBefore : [2, 1] (4)
                Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                Whitespace : None
            9) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 4] (7)
                                                    IterBefore : [2, 1] (4)
                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 1] (8)
                                                    IterBefore : [2, 4] (7)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 8
                                                                 Start : 7
                                                    Whitespace : None
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 1] (4)
                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            10) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 4] (7)
                                                                      IterBefore : [2, 1] (4)
                                                                      Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 1] (8)
                                                                      IterBefore : [2, 4] (7)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 8
                                                                                   Start : 7
                                                                      Whitespace : None
                                                    IterAfter  : [3, 1] (8)
                                                    IterBefore : [2, 1] (4)
                                                    Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 1] (4)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            11) 8, 9
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 2] (9)
                IterBefore : [3, 1] (8)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(8, 9), match='3'>
                Whitespace : None
            12) 9, 10
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 1] (10)
                IterBefore : [3, 2] (9)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 10
                             Start : 9
                Whitespace : None
            13) 8, 10
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 2] (9)
                                  IterBefore : [3, 1] (8)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(8, 9), match='3'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [4, 1] (10)
                                  IterBefore : [3, 2] (9)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 10
                                               Start : 9
                                  Whitespace : None
                IterAfter  : [4, 1] (10)
                IterBefore : [3, 1] (8)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            14) 8, 10
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 2] (9)
                                                    IterBefore : [3, 1] (8)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(8, 9), match='3'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [4, 1] (10)
                                                    IterBefore : [3, 2] (9)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 10
                                                                 Start : 9
                                                    Whitespace : None
                                  IterAfter  : [4, 1] (10)
                                  IterBefore : [3, 1] (8)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [4, 1] (10)
                IterBefore : [3, 1] (8)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            15) 8, 10
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 2] (9)
                                                                      IterBefore : [3, 1] (8)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(8, 9), match='3'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [4, 1] (10)
                                                                      IterBefore : [3, 2] (9)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 10
                                                                                   Start : 9
                                                                      Whitespace : None
                                                    IterAfter  : [4, 1] (10)
                                                    IterBefore : [3, 1] (8)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [4, 1] (10)
                                  IterBefore : [3, 1] (8)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [4, 1] (10)
                IterBefore : [3, 1] (8)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_SingleInclude(self):
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

        all_results = await ParseAsync(
            ["one"],
            self._phrases,
            observer,
            single_threaded=True,
        )

        assert len(all_results) == 2
        assert "one" in all_results
        assert "number" in all_results

        one_results = all_results["one"]

        assert str(one_results) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (4)
                                                                                    IterBefore : [1, 4] (3)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 4
                                                                                                 Start : 3
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (4)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 4] (7)
                                                                                    IterBefore : [2, 1] (4)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (8)
                                                                                    IterBefore : [2, 4] (7)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 8
                                                                                                 Start : 7
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (8)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 8] (15)
                                                                                    IterBefore : [3, 1] (8)
                                                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 15] (22)
                                                                                    IterBefore : [3, 9] (16)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                                                                                    Whitespace : 0)   15
                                                                                                 1)   16
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (23)
                                                                                    IterBefore : [3, 15] (22)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 23
                                                                                                 Start : 22
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (23)
                                                                  IterBefore : [3, 1] (8)
                                                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (23)
                                                IterBefore : [3, 1] (8)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (23)
                              IterBefore : [3, 1] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 2] (24)
                                                                                    IterBefore : [4, 1] (23)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 1] (25)
                                                                                    IterBefore : [4, 2] (24)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 25
                                                                                                 Start : 24
                                                                                    Whitespace : None
                                                                  IterAfter  : [5, 1] (25)
                                                                  IterBefore : [4, 1] (23)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [5, 1] (25)
                                                IterBefore : [4, 1] (23)
                                                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [5, 1] (25)
                              IterBefore : [4, 1] (23)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [5, 1] (25)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        number_results = all_results["number"]

        assert str(number_results) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 2] (1)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (2)
                                                                                    IterBefore : [1, 2] (1)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 2
                                                                                                 Start : 1
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (2)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (2)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (2)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 2] (3)
                                                                                    IterBefore : [2, 1] (2)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (4)
                                                                                    IterBefore : [2, 2] (3)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 4
                                                                                                 Start : 3
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (4)
                                                                  IterBefore : [2, 1] (2)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (4)
                                                IterBefore : [2, 1] (2)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (4)
                              IterBefore : [2, 1] (2)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 2] (5)
                                                                                    IterBefore : [3, 1] (4)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (6)
                                                                                    IterBefore : [3, 2] (5)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 6
                                                                                                 Start : 5
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (6)
                                                                  IterBefore : [3, 1] (4)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (6)
                                                IterBefore : [3, 1] (4)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (6)
                              IterBefore : [3, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (6)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert MethodCallsToString(
            observer.on_phrase_complete_mock,
            attribute_name="call_args_list",
        ) == textwrap.dedent(
            """\
            0) 0, 3
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [1, 4] (3)
                IterBefore : [1, 1] (0)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                Whitespace : None
            1) 3, 4
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 4] (3)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 4
                             Start : 3
                Whitespace : None
            2) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [1, 4] (3)
                                  IterBefore : [1, 1] (0)
                                  Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 4] (3)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 4
                                               Start : 3
                                  Whitespace : None
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            3) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [1, 4] (3)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 1] (4)
                                                    IterBefore : [1, 4] (3)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 4
                                                                 Start : 3
                                                    Whitespace : None
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 1] (0)
                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            4) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [1, 4] (3)
                                                                      IterBefore : [1, 1] (0)
                                                                      Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 1] (4)
                                                                      IterBefore : [1, 4] (3)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 4
                                                                                   Start : 3
                                                                      Whitespace : None
                                                    IterAfter  : [2, 1] (4)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 1] (0)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            5) 4, 7
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 4] (7)
                IterBefore : [2, 1] (4)
                Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                Whitespace : None
            6) 7, 8
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 4] (7)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 8
                             Start : 7
                Whitespace : None
            7) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 4] (7)
                                  IterBefore : [2, 1] (4)
                                  Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 4] (7)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 8
                                               Start : 7
                                  Whitespace : None
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            8) 4, 7
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 4] (7)
                IterBefore : [2, 1] (4)
                Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                Whitespace : None
            9) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 4] (7)
                                                    IterBefore : [2, 1] (4)
                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 1] (8)
                                                    IterBefore : [2, 4] (7)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 8
                                                                 Start : 7
                                                    Whitespace : None
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 1] (4)
                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            10) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 4] (7)
                                                                      IterBefore : [2, 1] (4)
                                                                      Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 1] (8)
                                                                      IterBefore : [2, 4] (7)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 8
                                                                                   Start : 7
                                                                      Whitespace : None
                                                    IterAfter  : [3, 1] (8)
                                                    IterBefore : [2, 1] (4)
                                                    Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 1] (4)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            11) 8, 15
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 8] (15)
                IterBefore : [3, 1] (8)
                Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                Whitespace : None
            12) 16, 22
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 15] (22)
                IterBefore : [3, 9] (16)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                Whitespace : 0)   15
                             1)   16
            13) 22, 23
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 1] (23)
                IterBefore : [3, 15] (22)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 23
                             Start : 22
                Whitespace : None
            14) 0, 1
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [1, 2] (1)
                IterBefore : [1, 1] (0)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                Whitespace : None
            15) 1, 2
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 1] (2)
                IterBefore : [1, 2] (1)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 2
                             Start : 1
                Whitespace : None
            16) 0, 2
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [1, 2] (1)
                                  IterBefore : [1, 1] (0)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 1] (2)
                                  IterBefore : [1, 2] (1)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 2
                                               Start : 1
                                  Whitespace : None
                IterAfter  : [2, 1] (2)
                IterBefore : [1, 1] (0)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            17) 0, 2
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [1, 2] (1)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 1] (2)
                                                    IterBefore : [1, 2] (1)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 2
                                                                 Start : 1
                                                    Whitespace : None
                                  IterAfter  : [2, 1] (2)
                                  IterBefore : [1, 1] (0)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [2, 1] (2)
                IterBefore : [1, 1] (0)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            18) 0, 2
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [1, 2] (1)
                                                                      IterBefore : [1, 1] (0)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 1] (2)
                                                                      IterBefore : [1, 2] (1)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 2
                                                                                   Start : 1
                                                                      Whitespace : None
                                                    IterAfter  : [2, 1] (2)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [2, 1] (2)
                                  IterBefore : [1, 1] (0)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [2, 1] (2)
                IterBefore : [1, 1] (0)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            19) 2, 3
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 2] (3)
                IterBefore : [2, 1] (2)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                Whitespace : None
            20) 3, 4
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 1] (4)
                IterBefore : [2, 2] (3)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 4
                             Start : 3
                Whitespace : None
            21) 2, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 2] (3)
                                  IterBefore : [2, 1] (2)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 1] (4)
                                  IterBefore : [2, 2] (3)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 4
                                               Start : 3
                                  Whitespace : None
                IterAfter  : [3, 1] (4)
                IterBefore : [2, 1] (2)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            22) 2, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 2] (3)
                                                    IterBefore : [2, 1] (2)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 1] (4)
                                                    IterBefore : [2, 2] (3)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 4
                                                                 Start : 3
                                                    Whitespace : None
                                  IterAfter  : [3, 1] (4)
                                  IterBefore : [2, 1] (2)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [3, 1] (4)
                IterBefore : [2, 1] (2)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            23) 2, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 2] (3)
                                                                      IterBefore : [2, 1] (2)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 1] (4)
                                                                      IterBefore : [2, 2] (3)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 4
                                                                                   Start : 3
                                                                      Whitespace : None
                                                    IterAfter  : [3, 1] (4)
                                                    IterBefore : [2, 1] (2)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [3, 1] (4)
                                  IterBefore : [2, 1] (2)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [3, 1] (4)
                IterBefore : [2, 1] (2)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            24) 4, 5
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 2] (5)
                IterBefore : [3, 1] (4)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                Whitespace : None
            25) 5, 6
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 1] (6)
                IterBefore : [3, 2] (5)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 6
                             Start : 5
                Whitespace : None
            26) 4, 6
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 2] (5)
                                  IterBefore : [3, 1] (4)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [4, 1] (6)
                                  IterBefore : [3, 2] (5)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 6
                                               Start : 5
                                  Whitespace : None
                IterAfter  : [4, 1] (6)
                IterBefore : [3, 1] (4)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            27) 4, 6
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 2] (5)
                                                    IterBefore : [3, 1] (4)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [4, 1] (6)
                                                    IterBefore : [3, 2] (5)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 6
                                                                 Start : 5
                                                    Whitespace : None
                                  IterAfter  : [4, 1] (6)
                                  IterBefore : [3, 1] (4)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [4, 1] (6)
                IterBefore : [3, 1] (4)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            28) 4, 6
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 2] (5)
                                                                      IterBefore : [3, 1] (4)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [4, 1] (6)
                                                                      IterBefore : [3, 2] (5)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 6
                                                                                   Start : 5
                                                                      Whitespace : None
                                                    IterAfter  : [4, 1] (6)
                                                    IterBefore : [3, 1] (4)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [4, 1] (6)
                                  IterBefore : [3, 1] (4)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [4, 1] (6)
                IterBefore : [3, 1] (4)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            29) 8, 15
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 8] (15)
                IterBefore : [3, 1] (8)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                Whitespace : None
            30) 8, 23
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 8] (15)
                                                    IterBefore : [3, 1] (8)
                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 15] (22)
                                                    IterBefore : [3, 9] (16)
                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                                                    Whitespace : 0)   15
                                                                 1)   16
                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [4, 1] (23)
                                                    IterBefore : [3, 15] (22)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 23
                                                                 Start : 22
                                                    Whitespace : None
                                  IterAfter  : [4, 1] (23)
                                  IterBefore : [3, 1] (8)
                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [4, 1] (23)
                IterBefore : [3, 1] (8)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            31) 8, 23
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 8] (15)
                                                                      IterBefore : [3, 1] (8)
                                                                      Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 15] (22)
                                                                      IterBefore : [3, 9] (16)
                                                                      Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                                                                      Whitespace : 0)   15
                                                                                   1)   16
                                                                 2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [4, 1] (23)
                                                                      IterBefore : [3, 15] (22)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 23
                                                                                   Start : 22
                                                                      Whitespace : None
                                                    IterAfter  : [4, 1] (23)
                                                    IterBefore : [3, 1] (8)
                                                    Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [4, 1] (23)
                                  IterBefore : [3, 1] (8)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [4, 1] (23)
                IterBefore : [3, 1] (8)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            32) 23, 24
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 2] (24)
                IterBefore : [4, 1] (23)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                Whitespace : None
            33) 24, 25
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [5, 1] (25)
                IterBefore : [4, 2] (24)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 25
                             Start : 24
                Whitespace : None
            34) 23, 25
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [4, 2] (24)
                                  IterBefore : [4, 1] (23)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [5, 1] (25)
                                  IterBefore : [4, 2] (24)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 25
                                               Start : 24
                                  Whitespace : None
                IterAfter  : [5, 1] (25)
                IterBefore : [4, 1] (23)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            35) 23, 24
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 2] (24)
                IterBefore : [4, 1] (23)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                Whitespace : None
            36) 23, 25
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [4, 2] (24)
                                                    IterBefore : [4, 1] (23)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [5, 1] (25)
                                                    IterBefore : [4, 2] (24)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 25
                                                                 Start : 24
                                                    Whitespace : None
                                  IterAfter  : [5, 1] (25)
                                  IterBefore : [4, 1] (23)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [5, 1] (25)
                IterBefore : [4, 1] (23)
                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            37) 23, 25
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [4, 2] (24)
                                                                      IterBefore : [4, 1] (23)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [5, 1] (25)
                                                                      IterBefore : [4, 2] (24)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 25
                                                                                   Start : 24
                                                                      Whitespace : None
                                                    IterAfter  : [5, 1] (25)
                                                    IterBefore : [4, 1] (23)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [5, 1] (25)
                                  IterBefore : [4, 1] (23)
                                  Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [5, 1] (25)
                IterBefore : [4, 1] (23)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_DoubleInclude(self):
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

        all_results = await ParseAsync(
            ["one"],
            self._phrases,
            observer,
            single_threaded=True,
        )

        assert len(all_results) == 2
        assert "one" in all_results
        assert "number" in all_results

        one_results = all_results["one"]

        assert str(one_results) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (4)
                                                                                    IterBefore : [1, 4] (3)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 4
                                                                                                 Start : 3
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (4)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 4] (7)
                                                                                    IterBefore : [2, 1] (4)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (8)
                                                                                    IterBefore : [2, 4] (7)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 8
                                                                                                 Start : 7
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (8)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 8] (15)
                                                                                    IterBefore : [3, 1] (8)
                                                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 15] (22)
                                                                                    IterBefore : [3, 9] (16)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                                                                                    Whitespace : 0)   15
                                                                                                 1)   16
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (23)
                                                                                    IterBefore : [3, 15] (22)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 23
                                                                                                 Start : 22
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (23)
                                                                  IterBefore : [3, 1] (8)
                                                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (23)
                                                IterBefore : [3, 1] (8)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (23)
                              IterBefore : [3, 1] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 2] (24)
                                                                                    IterBefore : [4, 1] (23)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 1] (25)
                                                                                    IterBefore : [4, 2] (24)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 25
                                                                                                 Start : 24
                                                                                    Whitespace : None
                                                                  IterAfter  : [5, 1] (25)
                                                                  IterBefore : [4, 1] (23)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [5, 1] (25)
                                                IterBefore : [4, 1] (23)
                                                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [5, 1] (25)
                              IterBefore : [4, 1] (23)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 8] (32)
                                                                                    IterBefore : [5, 1] (25)
                                                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(25, 32), match='include'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 15] (39)
                                                                                    IterBefore : [5, 9] (33)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(33, 39), match='number'>
                                                                                    Whitespace : 0)   32
                                                                                                 1)   33
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 1] (40)
                                                                                    IterBefore : [5, 15] (39)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 40
                                                                                                 Start : 39
                                                                                    Whitespace : None
                                                                  IterAfter  : [6, 1] (40)
                                                                  IterBefore : [5, 1] (25)
                                                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [6, 1] (40)
                                                IterBefore : [5, 1] (25)
                                                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [6, 1] (40)
                              IterBefore : [5, 1] (25)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 2] (41)
                                                                                    IterBefore : [6, 1] (40)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(40, 41), match='4'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [7, 1] (42)
                                                                                    IterBefore : [6, 2] (41)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 42
                                                                                                 Start : 41
                                                                                    Whitespace : None
                                                                  IterAfter  : [7, 1] (42)
                                                                  IterBefore : [6, 1] (40)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [7, 1] (42)
                                                IterBefore : [6, 1] (40)
                                                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [7, 1] (42)
                              IterBefore : [6, 1] (40)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [7, 1] (42)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert MethodCallsToString(
            observer.on_phrase_complete_mock,
            attribute_name="call_args_list",
        ) == textwrap.dedent(
            """\
            0) 0, 3
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [1, 4] (3)
                IterBefore : [1, 1] (0)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                Whitespace : None
            1) 3, 4
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 4] (3)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 4
                             Start : 3
                Whitespace : None
            2) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [1, 4] (3)
                                  IterBefore : [1, 1] (0)
                                  Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 4] (3)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 4
                                               Start : 3
                                  Whitespace : None
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            3) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [1, 4] (3)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 1] (4)
                                                    IterBefore : [1, 4] (3)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 4
                                                                 Start : 3
                                                    Whitespace : None
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 1] (0)
                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            4) 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [1, 4] (3)
                                                                      IterBefore : [1, 1] (0)
                                                                      Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 1] (4)
                                                                      IterBefore : [1, 4] (3)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 4
                                                                                   Start : 3
                                                                      Whitespace : None
                                                    IterAfter  : [2, 1] (4)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 1] (0)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            5) 4, 7
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 4] (7)
                IterBefore : [2, 1] (4)
                Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                Whitespace : None
            6) 7, 8
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 4] (7)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 8
                             Start : 7
                Whitespace : None
            7) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 4] (7)
                                  IterBefore : [2, 1] (4)
                                  Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 4] (7)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 8
                                               Start : 7
                                  Whitespace : None
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            8) 4, 7
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 4] (7)
                IterBefore : [2, 1] (4)
                Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                Whitespace : None
            9) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 4] (7)
                                                    IterBefore : [2, 1] (4)
                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 1] (8)
                                                    IterBefore : [2, 4] (7)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 8
                                                                 Start : 7
                                                    Whitespace : None
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 1] (4)
                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            10) 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 4] (7)
                                                                      IterBefore : [2, 1] (4)
                                                                      Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 1] (8)
                                                                      IterBefore : [2, 4] (7)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 8
                                                                                   Start : 7
                                                                      Whitespace : None
                                                    IterAfter  : [3, 1] (8)
                                                    IterBefore : [2, 1] (4)
                                                    Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 1] (4)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            11) 8, 15
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 8] (15)
                IterBefore : [3, 1] (8)
                Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                Whitespace : None
            12) 16, 22
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 15] (22)
                IterBefore : [3, 9] (16)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                Whitespace : 0)   15
                             1)   16
            13) 22, 23
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 1] (23)
                IterBefore : [3, 15] (22)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 23
                             Start : 22
                Whitespace : None
            14) 0, 1
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [1, 2] (1)
                IterBefore : [1, 1] (0)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                Whitespace : None
            15) 1, 2
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 1] (2)
                IterBefore : [1, 2] (1)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 2
                             Start : 1
                Whitespace : None
            16) 0, 2
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [1, 2] (1)
                                  IterBefore : [1, 1] (0)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 1] (2)
                                  IterBefore : [1, 2] (1)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 2
                                               Start : 1
                                  Whitespace : None
                IterAfter  : [2, 1] (2)
                IterBefore : [1, 1] (0)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            17) 0, 2
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [1, 2] (1)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 1] (2)
                                                    IterBefore : [1, 2] (1)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 2
                                                                 Start : 1
                                                    Whitespace : None
                                  IterAfter  : [2, 1] (2)
                                  IterBefore : [1, 1] (0)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [2, 1] (2)
                IterBefore : [1, 1] (0)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            18) 0, 2
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [1, 2] (1)
                                                                      IterBefore : [1, 1] (0)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 1] (2)
                                                                      IterBefore : [1, 2] (1)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 2
                                                                                   Start : 1
                                                                      Whitespace : None
                                                    IterAfter  : [2, 1] (2)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [2, 1] (2)
                                  IterBefore : [1, 1] (0)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [2, 1] (2)
                IterBefore : [1, 1] (0)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            19) 2, 3
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 2] (3)
                IterBefore : [2, 1] (2)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                Whitespace : None
            20) 3, 4
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 1] (4)
                IterBefore : [2, 2] (3)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 4
                             Start : 3
                Whitespace : None
            21) 2, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 2] (3)
                                  IterBefore : [2, 1] (2)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 1] (4)
                                  IterBefore : [2, 2] (3)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 4
                                               Start : 3
                                  Whitespace : None
                IterAfter  : [3, 1] (4)
                IterBefore : [2, 1] (2)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            22) 2, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 2] (3)
                                                    IterBefore : [2, 1] (2)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 1] (4)
                                                    IterBefore : [2, 2] (3)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 4
                                                                 Start : 3
                                                    Whitespace : None
                                  IterAfter  : [3, 1] (4)
                                  IterBefore : [2, 1] (2)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [3, 1] (4)
                IterBefore : [2, 1] (2)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            23) 2, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 2] (3)
                                                                      IterBefore : [2, 1] (2)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 1] (4)
                                                                      IterBefore : [2, 2] (3)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 4
                                                                                   Start : 3
                                                                      Whitespace : None
                                                    IterAfter  : [3, 1] (4)
                                                    IterBefore : [2, 1] (2)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [3, 1] (4)
                                  IterBefore : [2, 1] (2)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [3, 1] (4)
                IterBefore : [2, 1] (2)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            24) 4, 5
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 2] (5)
                IterBefore : [3, 1] (4)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                Whitespace : None
            25) 5, 6
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 1] (6)
                IterBefore : [3, 2] (5)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 6
                             Start : 5
                Whitespace : None
            26) 4, 6
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 2] (5)
                                  IterBefore : [3, 1] (4)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [4, 1] (6)
                                  IterBefore : [3, 2] (5)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 6
                                               Start : 5
                                  Whitespace : None
                IterAfter  : [4, 1] (6)
                IterBefore : [3, 1] (4)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            27) 4, 6
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 2] (5)
                                                    IterBefore : [3, 1] (4)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [4, 1] (6)
                                                    IterBefore : [3, 2] (5)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 6
                                                                 Start : 5
                                                    Whitespace : None
                                  IterAfter  : [4, 1] (6)
                                  IterBefore : [3, 1] (4)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [4, 1] (6)
                IterBefore : [3, 1] (4)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            28) 4, 6
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 2] (5)
                                                                      IterBefore : [3, 1] (4)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [4, 1] (6)
                                                                      IterBefore : [3, 2] (5)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 6
                                                                                   Start : 5
                                                                      Whitespace : None
                                                    IterAfter  : [4, 1] (6)
                                                    IterBefore : [3, 1] (4)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [4, 1] (6)
                                  IterBefore : [3, 1] (4)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [4, 1] (6)
                IterBefore : [3, 1] (4)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            29) 8, 15
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 8] (15)
                IterBefore : [3, 1] (8)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                Whitespace : None
            30) 8, 23
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 8] (15)
                                                    IterBefore : [3, 1] (8)
                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 15] (22)
                                                    IterBefore : [3, 9] (16)
                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                                                    Whitespace : 0)   15
                                                                 1)   16
                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [4, 1] (23)
                                                    IterBefore : [3, 15] (22)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 23
                                                                 Start : 22
                                                    Whitespace : None
                                  IterAfter  : [4, 1] (23)
                                  IterBefore : [3, 1] (8)
                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [4, 1] (23)
                IterBefore : [3, 1] (8)
                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            31) 8, 23
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 8] (15)
                                                                      IterBefore : [3, 1] (8)
                                                                      Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 15] (22)
                                                                      IterBefore : [3, 9] (16)
                                                                      Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                                                                      Whitespace : 0)   15
                                                                                   1)   16
                                                                 2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [4, 1] (23)
                                                                      IterBefore : [3, 15] (22)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 23
                                                                                   Start : 22
                                                                      Whitespace : None
                                                    IterAfter  : [4, 1] (23)
                                                    IterBefore : [3, 1] (8)
                                                    Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [4, 1] (23)
                                  IterBefore : [3, 1] (8)
                                  Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [4, 1] (23)
                IterBefore : [3, 1] (8)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            32) 23, 24
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 2] (24)
                IterBefore : [4, 1] (23)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                Whitespace : None
            33) 24, 25
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [5, 1] (25)
                IterBefore : [4, 2] (24)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 25
                             Start : 24
                Whitespace : None
            34) 23, 25
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [4, 2] (24)
                                  IterBefore : [4, 1] (23)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [5, 1] (25)
                                  IterBefore : [4, 2] (24)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 25
                                               Start : 24
                                  Whitespace : None
                IterAfter  : [5, 1] (25)
                IterBefore : [4, 1] (23)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            35) 23, 24
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 2] (24)
                IterBefore : [4, 1] (23)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                Whitespace : None
            36) 23, 25
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [4, 2] (24)
                                                    IterBefore : [4, 1] (23)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [5, 1] (25)
                                                    IterBefore : [4, 2] (24)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 25
                                                                 Start : 24
                                                    Whitespace : None
                                  IterAfter  : [5, 1] (25)
                                  IterBefore : [4, 1] (23)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [5, 1] (25)
                IterBefore : [4, 1] (23)
                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            37) 23, 25
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [4, 2] (24)
                                                                      IterBefore : [4, 1] (23)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [5, 1] (25)
                                                                      IterBefore : [4, 2] (24)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 25
                                                                                   Start : 24
                                                                      Whitespace : None
                                                    IterAfter  : [5, 1] (25)
                                                    IterBefore : [4, 1] (23)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [5, 1] (25)
                                  IterBefore : [4, 1] (23)
                                  Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [5, 1] (25)
                IterBefore : [4, 1] (23)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            38) 25, 32
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [5, 8] (32)
                IterBefore : [5, 1] (25)
                Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(25, 32), match='include'>
                Whitespace : None
            39) 33, 39
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [5, 15] (39)
                IterBefore : [5, 9] (33)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(33, 39), match='number'>
                Whitespace : 0)   32
                             1)   33
            40) 39, 40
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [6, 1] (40)
                IterBefore : [5, 15] (39)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 40
                             Start : 39
                Whitespace : None
            41) 25, 32
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [5, 8] (32)
                IterBefore : [5, 1] (25)
                Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(25, 32), match='include'>
                Whitespace : None
            42) 25, 40
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [5, 8] (32)
                                                    IterBefore : [5, 1] (25)
                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(25, 32), match='include'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [5, 15] (39)
                                                    IterBefore : [5, 9] (33)
                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(33, 39), match='number'>
                                                    Whitespace : 0)   32
                                                                 1)   33
                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [6, 1] (40)
                                                    IterBefore : [5, 15] (39)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 40
                                                                 Start : 39
                                                    Whitespace : None
                                  IterAfter  : [6, 1] (40)
                                  IterBefore : [5, 1] (25)
                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [6, 1] (40)
                IterBefore : [5, 1] (25)
                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            43) 25, 40
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [5, 8] (32)
                                                                      IterBefore : [5, 1] (25)
                                                                      Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(25, 32), match='include'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [5, 15] (39)
                                                                      IterBefore : [5, 9] (33)
                                                                      Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(33, 39), match='number'>
                                                                      Whitespace : 0)   32
                                                                                   1)   33
                                                                 2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [6, 1] (40)
                                                                      IterBefore : [5, 15] (39)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 40
                                                                                   Start : 39
                                                                      Whitespace : None
                                                    IterAfter  : [6, 1] (40)
                                                    IterBefore : [5, 1] (25)
                                                    Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [6, 1] (40)
                                  IterBefore : [5, 1] (25)
                                  Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [6, 1] (40)
                IterBefore : [5, 1] (25)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            44) 40, 41
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [6, 2] (41)
                IterBefore : [6, 1] (40)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(40, 41), match='4'>
                Whitespace : None
            45) 41, 42
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [7, 1] (42)
                IterBefore : [6, 2] (41)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 42
                             Start : 41
                Whitespace : None
            46) 40, 42
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [6, 2] (41)
                                  IterBefore : [6, 1] (40)
                                  Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(40, 41), match='4'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [7, 1] (42)
                                  IterBefore : [6, 2] (41)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 42
                                               Start : 41
                                  Whitespace : None
                IterAfter  : [7, 1] (42)
                IterBefore : [6, 1] (40)
                Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            47) 40, 41
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [6, 2] (41)
                IterBefore : [6, 1] (40)
                Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(40, 41), match='4'>
                Whitespace : None
            48) 40, 42
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [6, 2] (41)
                                                    IterBefore : [6, 1] (40)
                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(40, 41), match='4'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [7, 1] (42)
                                                    IterBefore : [6, 2] (41)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 42
                                                                 Start : 41
                                                    Whitespace : None
                                  IterAfter  : [7, 1] (42)
                                  IterBefore : [6, 1] (40)
                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [7, 1] (42)
                IterBefore : [6, 1] (40)
                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            49) 40, 42
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [6, 2] (41)
                                                                      IterBefore : [6, 1] (40)
                                                                      Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(40, 41), match='4'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [7, 1] (42)
                                                                      IterBefore : [6, 2] (41)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 42
                                                                                   Start : 41
                                                                      Whitespace : None
                                                    IterAfter  : [7, 1] (42)
                                                    IterBefore : [6, 1] (40)
                                                    Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [7, 1] (42)
                                  IterBefore : [6, 1] (40)
                                  Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [7, 1] (42)
                IterBefore : [6, 1] (40)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InvalidInclude(self):
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

        results = await ParseAsync(
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 1
        results = results[0]

        assert str(results) == "'invalid' could not be found"
        assert results.Line == 3
        assert results.Column == 1
        assert results.SourceName == "invalid"
        assert results.FullyQualifiedName == "one"

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MultipleFileSingleImport(self):
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

        results = await ParseAsync(
            ["one", "two"],
            self._phrases,
            observer,
        )

        assert len(results) == 3
        assert "one" in results
        assert "two" in results
        assert "number" in results

        one_results = results["one"]

        assert str(one_results) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (4)
                                                                                    IterBefore : [1, 4] (3)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 4
                                                                                                 Start : 3
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (4)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 4] (7)
                                                                                    IterBefore : [2, 1] (4)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (8)
                                                                                    IterBefore : [2, 4] (7)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 8
                                                                                                 Start : 7
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (8)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 8] (15)
                                                                                    IterBefore : [3, 1] (8)
                                                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 15), match='include'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 15] (22)
                                                                                    IterBefore : [3, 9] (16)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(16, 22), match='number'>
                                                                                    Whitespace : 0)   15
                                                                                                 1)   16
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (23)
                                                                                    IterBefore : [3, 15] (22)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 23
                                                                                                 Start : 22
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (23)
                                                                  IterBefore : [3, 1] (8)
                                                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (23)
                                                IterBefore : [3, 1] (8)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (23)
                              IterBefore : [3, 1] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 2] (24)
                                                                                    IterBefore : [4, 1] (23)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(23, 24), match='3'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 1] (25)
                                                                                    IterBefore : [4, 2] (24)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 25
                                                                                                 Start : 24
                                                                                    Whitespace : None
                                                                  IterAfter  : [5, 1] (25)
                                                                  IterBefore : [4, 1] (23)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [5, 1] (25)
                                                IterBefore : [4, 1] (23)
                                                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [5, 1] (25)
                              IterBefore : [4, 1] (23)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [5, 1] (25)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        two_results = results["two"]

        assert str(two_results) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='aaa'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (4)
                                                                                    IterBefore : [1, 4] (3)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 4
                                                                                                 Start : 3
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (4)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 5] (8)
                                                                                    IterBefore : [2, 1] (4)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 8), match='BBBB'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (9)
                                                                                    IterBefore : [2, 5] (8)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 9
                                                                                                 Start : 8
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (9)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (9)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (9)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 8] (16)
                                                                                    IterBefore : [3, 1] (9)
                                                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(9, 16), match='include'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 15] (23)
                                                                                    IterBefore : [3, 9] (17)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(17, 23), match='number'>
                                                                                    Whitespace : 0)   16
                                                                                                 1)   17
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (24)
                                                                                    IterBefore : [3, 15] (23)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 24
                                                                                                 Start : 23
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (24)
                                                                  IterBefore : [3, 1] (9)
                                                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (24)
                                                IterBefore : [3, 1] (9)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (24)
                              IterBefore : [3, 1] (9)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 7] (30)
                                                                                    IterBefore : [4, 1] (24)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(24, 30), match='cccccc'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 1] (31)
                                                                                    IterBefore : [4, 7] (30)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 31
                                                                                                 Start : 30
                                                                                    Whitespace : None
                                                                  IterAfter  : [5, 1] (31)
                                                                  IterBefore : [4, 1] (24)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [5, 1] (31)
                                                IterBefore : [4, 1] (24)
                                                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [5, 1] (31)
                              IterBefore : [4, 1] (24)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [5, 1] (31)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        number_results = results["number"]

        assert str(number_results) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 2] (1)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 1), match='4'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (2)
                                                                                    IterBefore : [1, 2] (1)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 2
                                                                                                 Start : 1
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (2)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (2)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (2)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 2] (3)
                                                                                    IterBefore : [2, 1] (2)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(2, 3), match='5'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (4)
                                                                                    IterBefore : [2, 2] (3)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 4
                                                                                                 Start : 3
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (4)
                                                                  IterBefore : [2, 1] (2)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (4)
                                                IterBefore : [2, 1] (2)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (4)
                              IterBefore : [2, 1] (2)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 2] (5)
                                                                                    IterBefore : [3, 1] (4)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 5), match='6'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (6)
                                                                                    IterBefore : [3, 2] (5)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 6
                                                                                                 Start : 5
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (6)
                                                                  IterBefore : [3, 1] (4)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (6)
                                                IterBefore : [3, 1] (4)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (6)
                              IterBefore : [3, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (6)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert len(observer.on_phrase_complete_mock.call_args_list) == 60

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InsertedPhrasesError(self):
        observer = self.CreateObserver(
            {
                "one" : textwrap.dedent(
                    """\
                    1 2 3
                    """,
                ),
            },
        )

        results = await ParseAsync(
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 1
        results = results[0]

        assert str(results) == "The syntax is not recognized"
        assert results.Line == 1
        assert results.Column == 2
        assert results.FullyQualifiedName == "one"

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InsertedPhrasesSuccess(self):
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

        results = await ParseAsync(
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 2
        assert "one" in results
        assert "number" in results

        one_results = results["one"]

        assert str(one_results) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 8] (7)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 7), match='include'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 15] (14)
                                                                                    IterBefore : [1, 9] (8)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 14), match='number'>
                                                                                    Whitespace : 0)   7
                                                                                                 1)   8
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (15)
                                                                                    IterBefore : [1, 15] (14)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 15
                                                                                                 Start : 14
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (15)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (15)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (15)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 2] (16)
                                                                                    IterBefore : [2, 1] (15)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(15, 16), match='1'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 4] (18)
                                                                                    IterBefore : [2, 3] (17)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(17, 18), match='2'>
                                                                                    Whitespace : 0)   16
                                                                                                 1)   17
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 6] (20)
                                                                                    IterBefore : [2, 5] (19)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(19, 20), match='3'>
                                                                                    Whitespace : 0)   18
                                                                                                 1)   19
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (21)
                                                                                    IterBefore : [2, 6] (20)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 21
                                                                                                 Start : 20
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (21)
                                                                  IterBefore : [2, 1] (15)
                                                                  Type       : Dynamic Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (21)
                                                IterBefore : [2, 1] (15)
                                                Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (21)
                              IterBefore : [2, 1] (15)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [3, 1] (21)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InsertedScopedPhrasesError(self):
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

        results = await ParseAsync(
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 1
        results = results[0]

        assert results.Line == 4
        assert results.Column == 2
        assert str(results) == "The syntax is not recognized"

        assert results.ToDebugString() == textwrap.dedent(
            """\
            The syntax is not recognized [4, 2]

            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 9] (8)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 10] (9)
                                                                                    IterBefore : [1, 9] (8)
                                                                                    Type       : Colon Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 9), match=':'>
                                                                                    Whitespace : None
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (10)
                                                                                    IterBefore : [1, 10] (9)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 10
                                                                                                 Start : 9
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 5] (14)
                                                                                    IterBefore : [2, 1] (10)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 14
                                                                                                 Start : 10
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [2, 12] (21)
                                                                                                                                          IterBefore : [2, 5] (14)
                                                                                                                                          Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(14, 21), match='include'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [2, 19] (28)
                                                                                                                                          IterBefore : [2, 13] (22)
                                                                                                                                          Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(22, 28), match='number'>
                                                                                                                                          Whitespace : 0)   21
                                                                                                                                                       1)   22
                                                                                                                                     2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 1] (29)
                                                                                                                                          IterBefore : [2, 19] (28)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 29
                                                                                                                                                       Start : 28
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [3, 1] (29)
                                                                                                                        IterBefore : [2, 5] (14)
                                                                                                                        Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [3, 1] (29)
                                                                                                      IterBefore : [2, 5] (14)
                                                                                                      Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [3, 1] (29)
                                                                                    IterBefore : [2, 5] (14)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 6] (34)
                                                                                                                                          IterBefore : [3, 5] (33)
                                                                                                                                          Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(33, 34), match='4'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 8] (36)
                                                                                                                                          IterBefore : [3, 7] (35)
                                                                                                                                          Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(35, 36), match='5'>
                                                                                                                                          Whitespace : 0)   34
                                                                                                                                                       1)   35
                                                                                                                                     2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 10] (38)
                                                                                                                                          IterBefore : [3, 9] (37)
                                                                                                                                          Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(37, 38), match='6'>
                                                                                                                                          Whitespace : 0)   36
                                                                                                                                                       1)   37
                                                                                                                                     3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [4, 1] (39)
                                                                                                                                          IterBefore : [3, 10] (38)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 39
                                                                                                                                                       Start : 38
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [4, 1] (39)
                                                                                                                        IterBefore : [3, 5] (33)
                                                                                                                        Type       : Dynamic Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [4, 1] (39)
                                                                                                      IterBefore : [3, 5] (33)
                                                                                                      Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [4, 1] (39)
                                                                                    IterBefore : [3, 5] (33)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (39)
                                                                                    IterBefore : [4, 1] (39)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (39)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : New Scope <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (39)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (39)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Include Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 2] (40)
                                                                                    IterBefore : [4, 1] (39)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(39, 40), match='7'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : [4, 1] (39)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : New Scope <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : None
                                                IterBefore : None
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : None
                              IterBefore : None
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : None
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_InsertedScopedPhrasesSuccess(self):
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

        results = await ParseAsync(
            ["one"],
            self._phrases,
            observer,
        )

        assert len(results) == 2
        assert "one" in results
        assert "number" in results

        one_results = results["one"]

        assert str(one_results) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 9] (8)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 10] (9)
                                                                                    IterBefore : [1, 9] (8)
                                                                                    Type       : Colon Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 9), match=':'>
                                                                                    Whitespace : None
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (10)
                                                                                    IterBefore : [1, 10] (9)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 10
                                                                                                 Start : 9
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 5] (14)
                                                                                    IterBefore : [2, 1] (10)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 14
                                                                                                 Start : 10
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [2, 12] (21)
                                                                                                                                          IterBefore : [2, 5] (14)
                                                                                                                                          Type       : Include Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(14, 21), match='include'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [2, 19] (28)
                                                                                                                                          IterBefore : [2, 13] (22)
                                                                                                                                          Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(22, 28), match='number'>
                                                                                                                                          Whitespace : 0)   21
                                                                                                                                                       1)   22
                                                                                                                                     2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 1] (29)
                                                                                                                                          IterBefore : [2, 19] (28)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 29
                                                                                                                                                       Start : 28
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [3, 1] (29)
                                                                                                                        IterBefore : [2, 5] (14)
                                                                                                                        Type       : Include <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [3, 1] (29)
                                                                                                      IterBefore : [2, 5] (14)
                                                                                                      Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [3, 1] (29)
                                                                                    IterBefore : [2, 5] (14)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 6] (34)
                                                                                                                                          IterBefore : [3, 5] (33)
                                                                                                                                          Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(33, 34), match='1'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 8] (36)
                                                                                                                                          IterBefore : [3, 7] (35)
                                                                                                                                          Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(35, 36), match='2'>
                                                                                                                                          Whitespace : 0)   34
                                                                                                                                                       1)   35
                                                                                                                                     2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 10] (38)
                                                                                                                                          IterBefore : [3, 9] (37)
                                                                                                                                          Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(37, 38), match='3'>
                                                                                                                                          Whitespace : 0)   36
                                                                                                                                                       1)   37
                                                                                                                                     3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [4, 1] (39)
                                                                                                                                          IterBefore : [3, 10] (38)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 39
                                                                                                                                                       Start : 38
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [4, 1] (39)
                                                                                                                        IterBefore : [3, 5] (33)
                                                                                                                        Type       : Dynamic Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [4, 1] (39)
                                                                                                      IterBefore : [3, 5] (33)
                                                                                                      Type       : (Include, Upper, Lower, Number, New Scope) / (Dynamic Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [4, 1] (39)
                                                                                    IterBefore : [3, 5] (33)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (39)
                                                                                    IterBefore : [4, 1] (39)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (39)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : New Scope <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (39)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Include, Upper, Lower, Number, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (39)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (39)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

# ----------------------------------------------------------------------
def test_NodeStrNoChildren():
    node = Node(CreatePhrase(name="Phrase", item=NewlineToken()))

    assert str(node) == textwrap.dedent(
        """\
        <class 'TheLanguage.Parser.Components.AST.Node'>
        Children   : -- empty list --
        IterAfter  : None
        IterBefore : None
        Type       : Phrase <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
        """,
    )

# TODO: Circular dependencies
