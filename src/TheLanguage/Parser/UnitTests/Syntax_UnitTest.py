# ----------------------------------------------------------------------
# |
# |  Syntax_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-22 10:18:14
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

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from unittest.mock import Mock

import pytest

from asynctest import CoroutineMock
from semantic_version import Version as SemVer

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Syntax import *
    from ..TranslationUnitsParser import ParseAsync

    from ..Components.ThreadPool import CreateThreadPool


# ----------------------------------------------------------------------
class TestStandard(object):

    _upper_token                            = RegexToken("Upper Token", re.compile(r"(?P<value>[A-Z]+)"))
    _lower_token                            = RegexToken("Lower Token", re.compile(r"(?P<value>[a-z]+)"))
    _number_token                           = RegexToken("Number Token", re.compile(r"(?P<value>[0-9]+)"))

    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number Phrase", item=[_number_token, NewlineToken()])

    _syntaxes                               = {
        SemVer("1.0.0") : DynamicPhrasesInfo([], [], [_upper_phrase, _lower_phrase], []),
        SemVer("2.0.0") : DynamicPhrasesInfo([], [], [_upper_phrase, _lower_phrase, _number_phrase], []),
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

        mock.OnIndentAsync = CoroutineMock()
        mock.OnDedentAsync = CoroutineMock()
        mock.OnPhraseCompleteAsync = CoroutineMock()

        return Observer(mock, cls._syntaxes)

    # ----------------------------------------------------------------------
    def test_Properties(self):
        observer = self.CreateObserver({})

        assert observer.DefaultVersion == SemVer("2.0.0")

        assert len(observer.Syntaxes) == 2

        # The syntax statements should have been added to each
        assert len(observer.Syntaxes[SemVer("1.0.0")].Statements) == 4
        assert len(observer.Syntaxes[SemVer("2.0.0")].Statements) == 5

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

        result = await ParseAsync(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

        assert len(result) == 1
        assert "one" in result
        result = result["one"]

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 1] (0)
                                                                                    IterEnd    : [1, 6] (5)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 5), match='UPPER'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 6] (5)
                                                                                    IterEnd    : [2, 1] (6)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 6
                                                                                                 Start : 5
                                                                                    Whitespace : None
                                                                  IterBegin_ : [1, 1] (0)
                                                                  IterEnd    : [2, 1] (6)
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [1, 1] (0)
                                                IterEnd    : [2, 1] (6)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [1, 1] (0)
                              IterEnd    : [2, 1] (6)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [2, 1] (6)
                                                                                    IterEnd    : [2, 6] (11)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(6, 11), match='lower'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [2, 6] (11)
                                                                                    IterEnd    : [3, 1] (12)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 12
                                                                                                 Start : 11
                                                                                    Whitespace : None
                                                                  IterBegin_ : [2, 1] (6)
                                                                  IterEnd    : [3, 1] (12)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [2, 1] (6)
                                                IterEnd    : [3, 1] (12)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [2, 1] (6)
                              IterEnd    : [3, 1] (12)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [3, 1] (12)
                                                                                    IterEnd    : [3, 5] (16)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(12, 16), match='1234'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [3, 5] (16)
                                                                                    IterEnd    : [4, 1] (17)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 17
                                                                                                 Start : 16
                                                                                    Whitespace : None
                                                                  IterBegin_ : [3, 1] (12)
                                                                  IterEnd    : [4, 1] (17)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [3, 1] (12)
                                                IterEnd    : [4, 1] (17)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [3, 1] (12)
                              IterEnd    : [4, 1] (17)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterBegin_ : [1, 1] (0)
            IterEnd    : [4, 1] (17)
            Type       : <None>
            """,
        )

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

        result = await ParseAsync(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

        assert len(result) == 1
        assert "one" in result
        result = result["one"]

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 1] (0)
                                                                                    IterEnd    : [1, 7] (6)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 6), match='AUPPER'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 7] (6)
                                                                                    IterEnd    : [2, 1] (7)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 7
                                                                                                 Start : 6
                                                                                    Whitespace : None
                                                                  IterBegin_ : [1, 1] (0)
                                                                  IterEnd    : [2, 1] (7)
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [1, 1] (0)
                                                IterEnd    : [2, 1] (7)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [1, 1] (0)
                              IterEnd    : [2, 1] (7)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [2, 1] (7)
                                                                                    IterEnd    : [2, 7] (13)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(7, 13), match='alower'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [2, 7] (13)
                                                                                    IterEnd    : [3, 1] (14)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 14
                                                                                                 Start : 13
                                                                                    Whitespace : None
                                                                  IterBegin_ : [2, 1] (7)
                                                                  IterEnd    : [3, 1] (14)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [2, 1] (7)
                                                IterEnd    : [3, 1] (14)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [2, 1] (7)
                              IterEnd    : [3, 1] (14)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [3, 1] (14)
                                                                                    IterEnd    : [3, 5] (18)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(14, 18), match='1234'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [3, 5] (18)
                                                                                    IterEnd    : [5, 1] (20)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 20
                                                                                                 Start : 18
                                                                                    Whitespace : None
                                                                  IterBegin_ : [3, 1] (14)
                                                                  IterEnd    : [5, 1] (20)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [3, 1] (14)
                                                IterEnd    : [5, 1] (20)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [3, 1] (14)
                              IterEnd    : [5, 1] (20)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 1] (20)
                                                                                    IterEnd    : [5, 7] (26)
                                                                                    Type       : '__with' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(20, 26), match='__with'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 8] (27)
                                                                                    IterEnd    : [5, 16] (35)
                                                                                    Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(27, 35), match='__syntax'>
                                                                                    Whitespace : 0)   26
                                                                                                 1)   27
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 16] (35)
                                                                                    IterEnd    : [5, 17] (36)
                                                                                    Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(35, 36), match='='>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 17] (36)
                                                                                    IterEnd    : [5, 20] (39)
                                                                                    Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(36, 39), match='1.0'>
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 20] (39)
                                                                                    IterEnd    : [5, 21] (40)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(39, 40), match=':'>
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 21] (40)
                                                                                    IterEnd    : [6, 1] (41)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 41
                                                                                                 Start : 40
                                                                                    Whitespace : None
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [6, 1] (41)
                                                                                    IterEnd    : [6, 5] (45)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 45
                                                                                                 Start : 41
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               7)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [6, 5] (45)
                                                                                                                                                            IterEnd    : [6, 11] (51)
                                                                                                                                                            Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(45, 51), match='BUPPER'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [6, 11] (51)
                                                                                                                                                            IterEnd    : [7, 1] (52)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 52
                                                                                                                                                                         Start : 51
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [6, 5] (45)
                                                                                                                                          IterEnd    : [7, 1] (52)
                                                                                                                                          Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [6, 5] (45)
                                                                                                                        IterEnd    : [7, 1] (52)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [6, 5] (45)
                                                                                                      IterEnd    : [7, 1] (52)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [7, 5] (56)
                                                                                                                                                            IterEnd    : [7, 11] (62)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(56, 62), match='blower'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [7, 11] (62)
                                                                                                                                                            IterEnd    : [9, 1] (64)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 64
                                                                                                                                                                         Start : 62
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [7, 5] (56)
                                                                                                                                          IterEnd    : [9, 1] (64)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [7, 5] (56)
                                                                                                                        IterEnd    : [9, 1] (64)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [7, 5] (56)
                                                                                                      IterEnd    : [9, 1] (64)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterBegin_ : [6, 5] (45)
                                                                                    IterEnd    : [9, 1] (64)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               8)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [9, 1] (64)
                                                                                    IterEnd    : [9, 1] (64)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterBegin_ : [5, 1] (20)
                                                                  IterEnd    : [9, 1] (64)
                                                                  Type       : Set Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [5, 1] (20)
                                                IterEnd    : [9, 1] (64)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [5, 1] (20)
                              IterEnd    : [9, 1] (64)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [9, 1] (64)
                                                                                    IterEnd    : [9, 7] (70)
                                                                                    Type       : '__with' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(64, 70), match='__with'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [9, 8] (71)
                                                                                    IterEnd    : [9, 16] (79)
                                                                                    Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(71, 79), match='__syntax'>
                                                                                    Whitespace : 0)   70
                                                                                                 1)   71
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [9, 16] (79)
                                                                                    IterEnd    : [9, 17] (80)
                                                                                    Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(79, 80), match='='>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [9, 17] (80)
                                                                                    IterEnd    : [9, 22] (85)
                                                                                    Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(80, 85), match='1.0.0'>
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [9, 22] (85)
                                                                                    IterEnd    : [9, 23] (86)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(85, 86), match=':'>
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [9, 23] (86)
                                                                                    IterEnd    : [10, 1] (87)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 87
                                                                                                 Start : 86
                                                                                    Whitespace : None
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [10, 1] (87)
                                                                                    IterEnd    : [10, 5] (91)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 91
                                                                                                 Start : 87
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               7)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [10, 5] (91)
                                                                                                                                                            IterEnd    : [10, 11] (97)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(91, 97), match='clower'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [10, 11] (97)
                                                                                                                                                            IterEnd    : [12, 1] (99)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 99
                                                                                                                                                                         Start : 97
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [10, 5] (91)
                                                                                                                                          IterEnd    : [12, 1] (99)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [10, 5] (91)
                                                                                                                        IterEnd    : [12, 1] (99)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [10, 5] (91)
                                                                                                      IterEnd    : [12, 1] (99)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterBegin_ : [10, 5] (91)
                                                                                    IterEnd    : [12, 1] (99)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               8)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [12, 1] (99)
                                                                                    IterEnd    : [12, 1] (99)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterBegin_ : [9, 1] (64)
                                                                  IterEnd    : [12, 1] (99)
                                                                  Type       : Set Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [9, 1] (64)
                                                IterEnd    : [12, 1] (99)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [9, 1] (64)
                              IterEnd    : [12, 1] (99)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [12, 1] (99)
                                                                                    IterEnd    : [12, 7] (105)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(99, 105), match='456789'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [12, 7] (105)
                                                                                    IterEnd    : [13, 1] (106)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 106
                                                                                                 Start : 105
                                                                                    Whitespace : None
                                                                  IterBegin_ : [12, 1] (99)
                                                                  IterEnd    : [13, 1] (106)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [12, 1] (99)
                                                IterEnd    : [13, 1] (106)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [12, 1] (99)
                              IterEnd    : [13, 1] (106)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterBegin_ : [1, 1] (0)
            IterEnd    : [13, 1] (106)
            Type       : <None>
            """,
        )

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

        result = await ParseAsync(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

        assert len(result) == 1
        result = result[0]

        assert str(result) == "The syntax is not recognized"
        assert result.FullyQualifiedName == "one"
        assert result.Line == 8
        assert result.Column == 1

        assert result.ToDebugString() == textwrap.dedent(
            """\
            The syntax is not recognized [8, 1]

            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 1] (0)
                                                                                    IterEnd    : [1, 7] (6)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 6), match='AUPPER'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 7] (6)
                                                                                    IterEnd    : [2, 1] (7)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 7
                                                                                                 Start : 6
                                                                                    Whitespace : None
                                                                  IterBegin_ : [1, 1] (0)
                                                                  IterEnd    : [2, 1] (7)
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [1, 1] (0)
                                                IterEnd    : [2, 1] (7)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [1, 1] (0)
                              IterEnd    : [2, 1] (7)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [2, 1] (7)
                                                                                    IterEnd    : [2, 7] (13)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(7, 13), match='alower'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [2, 7] (13)
                                                                                    IterEnd    : [3, 1] (14)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 14
                                                                                                 Start : 13
                                                                                    Whitespace : None
                                                                  IterBegin_ : [2, 1] (7)
                                                                  IterEnd    : [3, 1] (14)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [2, 1] (7)
                                                IterEnd    : [3, 1] (14)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [2, 1] (7)
                              IterEnd    : [3, 1] (14)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [3, 1] (14)
                                                                                    IterEnd    : [3, 5] (18)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(14, 18), match='1234'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [3, 5] (18)
                                                                                    IterEnd    : [5, 1] (20)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 20
                                                                                                 Start : 18
                                                                                    Whitespace : None
                                                                  IterBegin_ : [3, 1] (14)
                                                                  IterEnd    : [5, 1] (20)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [3, 1] (14)
                                                IterEnd    : [5, 1] (20)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [3, 1] (14)
                              IterEnd    : [5, 1] (20)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterBegin_ : None
                                                                                    IterEnd    : None
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterBegin_ : None
                                                                  IterEnd    : None
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 1] (20)
                                                                                    IterEnd    : [5, 7] (26)
                                                                                    Type       : '__with' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(20, 26), match='__with'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 8] (27)
                                                                                    IterEnd    : [5, 16] (35)
                                                                                    Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(27, 35), match='__syntax'>
                                                                                    Whitespace : 0)   26
                                                                                                 1)   27
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 16] (35)
                                                                                    IterEnd    : [5, 17] (36)
                                                                                    Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(35, 36), match='='>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 17] (36)
                                                                                    IterEnd    : [5, 20] (39)
                                                                                    Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(36, 39), match='1.0'>
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 20] (39)
                                                                                    IterEnd    : [5, 21] (40)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(39, 40), match=':'>
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 21] (40)
                                                                                    IterEnd    : [6, 1] (41)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 41
                                                                                                 Start : 40
                                                                                    Whitespace : None
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [6, 1] (41)
                                                                                    IterEnd    : [6, 5] (45)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 45
                                                                                                 Start : 41
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               7)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [6, 5] (45)
                                                                                                                                                            IterEnd    : [6, 11] (51)
                                                                                                                                                            Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(45, 51), match='BUPPER'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [6, 11] (51)
                                                                                                                                                            IterEnd    : [7, 1] (52)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 52
                                                                                                                                                                         Start : 51
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [6, 5] (45)
                                                                                                                                          IterEnd    : [7, 1] (52)
                                                                                                                                          Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [6, 5] (45)
                                                                                                                        IterEnd    : [7, 1] (52)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [6, 5] (45)
                                                                                                      IterEnd    : [7, 1] (52)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [7, 5] (56)
                                                                                                                                                            IterEnd    : [7, 11] (62)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(56, 62), match='blower'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [7, 11] (62)
                                                                                                                                                            IterEnd    : [8, 1] (63)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 63
                                                                                                                                                                         Start : 62
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [7, 5] (56)
                                                                                                                                          IterEnd    : [8, 1] (63)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [7, 5] (56)
                                                                                                                        IterEnd    : [8, 1] (63)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [7, 5] (56)
                                                                                                      IterEnd    : [8, 1] (63)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterBegin_ : [6, 5] (45)
                                                                                    IterEnd    : [8, 1] (63)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterBegin_ : None
                                                                                    IterEnd    : None
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterBegin_ : [5, 1] (20)
                                                                  IterEnd    : None
                                                                  Type       : Set Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterBegin_ : None
                                                                                    IterEnd    : None
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterBegin_ : None
                                                                  IterEnd    : None
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterBegin_ : None
                                                                                    IterEnd    : None
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterBegin_ : None
                                                                  IterEnd    : None
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterBegin_ : None
                                                                                    IterEnd    : None
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterBegin_ : None
                                                                  IterEnd    : None
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : None
                                                IterEnd    : None
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : None
                              IterEnd    : None
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterBegin_ : [1, 1] (0)
            IterEnd    : None
            Type       : <None>
            """,
        )

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

        result = await ParseAsync(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

        assert len(result) == 1
        result = result[0]

        assert str(result) == "The syntax version '4.5.6' is not recognized"
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

        result = await ParseAsync(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

        assert len(result) == 1
        result = result[0]

        assert str(result) == "The syntax version '4.5.0' is not recognized"
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

        result = await ParseAsync(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

        assert len(result) == 1
        result = result[0]

        assert str(result) == "The syntax version 'this_is_not_a_valid_version' is not a valid version"
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

        result = await ParseAsync(["one"], observer.Syntaxes[observer.DefaultVersion], observer)

        assert len(result) == 1
        result = result["one"]

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 1] (0)
                                                                                    IterEnd    : [1, 5] (4)
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 4), match='__if'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterBegin_ : [1, 6] (5)
                                                                                                                        IterEnd    : [1, 14] (13)
                                                                                                                        Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(5, 13), match='__syntax'>
                                                                                                                        Whitespace : 0)   4
                                                                                                                                     1)   5
                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterBegin_ : [1, 15] (14)
                                                                                                                                          IterEnd    : [1, 17] (16)
                                                                                                                                          Type       : '==' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(14, 16), match='=='>
                                                                                                                                          Whitespace : 0)   13
                                                                                                                                                       1)   14
                                                                                                                        IterBegin_ : [1, 15] (14)
                                                                                                                        IterEnd    : [1, 17] (16)
                                                                                                                        Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterBegin_ : [1, 18] (17)
                                                                                                                        IterEnd    : [1, 23] (22)
                                                                                                                        Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(17, 22), match='1.2.3'>
                                                                                                                        Whitespace : 0)   16
                                                                                                                                     1)   17
                                                                                                      IterBegin_ : [1, 6] (5)
                                                                                                      IterEnd    : [1, 23] (22)
                                                                                                      Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                    IterBegin_ : [1, 6] (5)
                                                                                    IterEnd    : [1, 23] (22)
                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 23] (22)
                                                                                    IterEnd    : [1, 24] (23)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(22, 23), match=':'>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [1, 24] (23)
                                                                                    IterEnd    : [2, 1] (24)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 24
                                                                                                 Start : 23
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [2, 1] (24)
                                                                                    IterEnd    : [2, 5] (28)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 28
                                                                                                 Start : 24
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [2, 5] (28)
                                                                                                                                                            IterEnd    : [2, 9] (32)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(28, 32), match='fooa'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [2, 9] (32)
                                                                                                                                                            IterEnd    : [4, 1] (34)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 34
                                                                                                                                                                         Start : 32
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [2, 5] (28)
                                                                                                                                          IterEnd    : [4, 1] (34)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [2, 5] (28)
                                                                                                                        IterEnd    : [4, 1] (34)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [2, 5] (28)
                                                                                                      IterEnd    : [4, 1] (34)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterBegin_ : [2, 5] (28)
                                                                                    IterEnd    : [4, 1] (34)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [4, 1] (34)
                                                                                    IterEnd    : [4, 1] (34)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterBegin_ : [1, 1] (0)
                                                                  IterEnd    : [4, 1] (34)
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [1, 1] (0)
                                                IterEnd    : [4, 1] (34)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [1, 1] (0)
                              IterEnd    : [4, 1] (34)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [4, 1] (34)
                                                                                    IterEnd    : [4, 5] (38)
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(34, 38), match='__if'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterBegin_ : [4, 6] (39)
                                                                                                                        IterEnd    : [4, 9] (42)
                                                                                                                        Type       : 'not' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(39, 42), match='not'>
                                                                                                                        Whitespace : 0)   38
                                                                                                                                     1)   39
                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [4, 10] (43)
                                                                                                                                                            IterEnd    : [4, 18] (51)
                                                                                                                                                            Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(43, 51), match='__syntax'>
                                                                                                                                                            Whitespace : 0)   42
                                                                                                                                                                         1)   43
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterBegin_ : [4, 19] (52)
                                                                                                                                                                              IterEnd    : [4, 21] (54)
                                                                                                                                                                              Type       : '==' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(52, 54), match='=='>
                                                                                                                                                                              Whitespace : 0)   51
                                                                                                                                                                                           1)   52
                                                                                                                                                            IterBegin_ : [4, 19] (52)
                                                                                                                                                            IterEnd    : [4, 21] (54)
                                                                                                                                                            Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [4, 22] (55)
                                                                                                                                                            IterEnd    : [4, 25] (58)
                                                                                                                                                            Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(55, 58), match='4.0'>
                                                                                                                                                            Whitespace : 0)   54
                                                                                                                                                                         1)   55
                                                                                                                                          IterBegin_ : [4, 10] (43)
                                                                                                                                          IterEnd    : [4, 25] (58)
                                                                                                                                          Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [4, 10] (43)
                                                                                                                        IterEnd    : [4, 25] (58)
                                                                                                                        Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [4, 6] (39)
                                                                                                      IterEnd    : [4, 25] (58)
                                                                                                      Type       : Not <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                    IterBegin_ : [4, 6] (39)
                                                                                    IterEnd    : [4, 25] (58)
                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [4, 25] (58)
                                                                                    IterEnd    : [4, 26] (59)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(58, 59), match=':'>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [4, 26] (59)
                                                                                    IterEnd    : [5, 1] (60)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 60
                                                                                                 Start : 59
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [5, 1] (60)
                                                                                    IterEnd    : [5, 5] (64)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 64
                                                                                                 Start : 60
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [5, 5] (64)
                                                                                                                                                            IterEnd    : [5, 9] (68)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(64, 68), match='foob'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [5, 9] (68)
                                                                                                                                                            IterEnd    : [7, 1] (70)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 70
                                                                                                                                                                         Start : 68
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [5, 5] (64)
                                                                                                                                          IterEnd    : [7, 1] (70)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [5, 5] (64)
                                                                                                                        IterEnd    : [7, 1] (70)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [5, 5] (64)
                                                                                                      IterEnd    : [7, 1] (70)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterBegin_ : [5, 5] (64)
                                                                                    IterEnd    : [7, 1] (70)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [7, 1] (70)
                                                                                    IterEnd    : [7, 1] (70)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterBegin_ : [4, 1] (34)
                                                                  IterEnd    : [7, 1] (70)
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [4, 1] (34)
                                                IterEnd    : [7, 1] (70)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [4, 1] (34)
                              IterEnd    : [7, 1] (70)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [7, 1] (70)
                                                                                    IterEnd    : [7, 5] (74)
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(70, 74), match='__if'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterBegin_ : [7, 6] (75)
                                                                                                                        IterEnd    : [7, 7] (76)
                                                                                                                        Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(75, 76), match='('>
                                                                                                                        Whitespace : 0)   74
                                                                                                                                     1)   75
                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [7, 7] (76)
                                                                                                                                                            IterEnd    : [7, 15] (84)
                                                                                                                                                            Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(76, 84), match='__syntax'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterBegin_ : [7, 16] (85)
                                                                                                                                                                              IterEnd    : [7, 17] (86)
                                                                                                                                                                              Type       : '<' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(85, 86), match='<'>
                                                                                                                                                                              Whitespace : 0)   84
                                                                                                                                                                                           1)   85
                                                                                                                                                            IterBegin_ : [7, 16] (85)
                                                                                                                                                            IterEnd    : [7, 17] (86)
                                                                                                                                                            Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [7, 18] (87)
                                                                                                                                                            IterEnd    : [7, 21] (90)
                                                                                                                                                            Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(87, 90), match='1.0'>
                                                                                                                                                            Whitespace : 0)   86
                                                                                                                                                                         1)   87
                                                                                                                                          IterBegin_ : [7, 7] (76)
                                                                                                                                          IterEnd    : [7, 21] (90)
                                                                                                                                          Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [7, 7] (76)
                                                                                                                        IterEnd    : [7, 21] (90)
                                                                                                                        Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterBegin_ : [7, 22] (91)
                                                                                                                                                                              IterEnd    : [7, 25] (94)
                                                                                                                                                                              Type       : 'and' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(91, 94), match='and'>
                                                                                                                                                                              Whitespace : 0)   90
                                                                                                                                                                                           1)   91
                                                                                                                                                            IterBegin_ : [7, 22] (91)
                                                                                                                                                            IterEnd    : [7, 25] (94)
                                                                                                                                                            Type       : Or: ('and', 'or') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                IterBegin_ : [7, 26] (95)
                                                                                                                                                                                                IterEnd    : [7, 34] (103)
                                                                                                                                                                                                Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(95, 103), match='__syntax'>
                                                                                                                                                                                                Whitespace : 0)   94
                                                                                                                                                                                                             1)   95
                                                                                                                                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                  IsIgnored  : False
                                                                                                                                                                                                                  IterBegin_ : [7, 35] (104)
                                                                                                                                                                                                                  IterEnd    : [7, 36] (105)
                                                                                                                                                                                                                  Type       : '>' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                               Match : <_sre.SRE_Match object; span=(104, 105), match='>'>
                                                                                                                                                                                                                  Whitespace : 0)   103
                                                                                                                                                                                                                               1)   104
                                                                                                                                                                                                IterBegin_ : [7, 35] (104)
                                                                                                                                                                                                IterEnd    : [7, 36] (105)
                                                                                                                                                                                                Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                IterBegin_ : [7, 37] (106)
                                                                                                                                                                                                IterEnd    : [7, 40] (109)
                                                                                                                                                                                                Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(106, 109), match='2.0'>
                                                                                                                                                                                                Whitespace : 0)   105
                                                                                                                                                                                                             1)   106
                                                                                                                                                                              IterBegin_ : [7, 26] (95)
                                                                                                                                                                              IterEnd    : [7, 40] (109)
                                                                                                                                                                              Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                            IterBegin_ : [7, 26] (95)
                                                                                                                                                            IterEnd    : [7, 40] (109)
                                                                                                                                                            Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                          IterBegin_ : [7, 22] (91)
                                                                                                                                          IterEnd    : [7, 40] (109)
                                                                                                                                          Type       : Sequence: [Or: ('and', 'or'), Condition Phrase] <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [7, 22] (91)
                                                                                                                        IterEnd    : [7, 40] (109)
                                                                                                                        Type       : Repeat: {Sequence: [Or: ('and', 'or'), Condition Phrase], 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                   3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterBegin_ : [7, 40] (109)
                                                                                                                        IterEnd    : [7, 41] (110)
                                                                                                                        Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(109, 110), match=')'>
                                                                                                                        Whitespace : None
                                                                                                      IterBegin_ : [7, 6] (75)
                                                                                                      IterEnd    : [7, 41] (110)
                                                                                                      Type       : Logical <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                    IterBegin_ : [7, 6] (75)
                                                                                    IterEnd    : [7, 41] (110)
                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [7, 41] (110)
                                                                                    IterEnd    : [7, 42] (111)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(110, 111), match=':'>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [7, 42] (111)
                                                                                    IterEnd    : [8, 1] (112)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 112
                                                                                                 Start : 111
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [8, 1] (112)
                                                                                    IterEnd    : [8, 5] (116)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 116
                                                                                                 Start : 112
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [8, 5] (116)
                                                                                                                                                            IterEnd    : [8, 9] (120)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(116, 120), match='fooc'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [8, 9] (120)
                                                                                                                                                            IterEnd    : [10, 1] (122)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 122
                                                                                                                                                                         Start : 120
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [8, 5] (116)
                                                                                                                                          IterEnd    : [10, 1] (122)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [8, 5] (116)
                                                                                                                        IterEnd    : [10, 1] (122)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [8, 5] (116)
                                                                                                      IterEnd    : [10, 1] (122)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterBegin_ : [8, 5] (116)
                                                                                    IterEnd    : [10, 1] (122)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [10, 1] (122)
                                                                                    IterEnd    : [10, 1] (122)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterBegin_ : [7, 1] (70)
                                                                  IterEnd    : [10, 1] (122)
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [7, 1] (70)
                                                IterEnd    : [10, 1] (122)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [7, 1] (70)
                              IterEnd    : [10, 1] (122)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [10, 1] (122)
                                                                                    IterEnd    : [10, 5] (126)
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(122, 126), match='__if'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterBegin_ : [10, 6] (127)
                                                                                                                        IterEnd    : [10, 7] (128)
                                                                                                                        Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(127, 128), match='('>
                                                                                                                        Whitespace : 0)   126
                                                                                                                                     1)   127
                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [10, 7] (128)
                                                                                                                                                            IterEnd    : [10, 15] (136)
                                                                                                                                                            Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(128, 136), match='__syntax'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterBegin_ : [10, 16] (137)
                                                                                                                                                                              IterEnd    : [10, 18] (139)
                                                                                                                                                                              Type       : '!=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(137, 139), match='!='>
                                                                                                                                                                              Whitespace : 0)   136
                                                                                                                                                                                           1)   137
                                                                                                                                                            IterBegin_ : [10, 16] (137)
                                                                                                                                                            IterEnd    : [10, 18] (139)
                                                                                                                                                            Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [10, 19] (140)
                                                                                                                                                            IterEnd    : [10, 22] (143)
                                                                                                                                                            Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(140, 143), match='2.0'>
                                                                                                                                                            Whitespace : 0)   139
                                                                                                                                                                         1)   140
                                                                                                                                          IterBegin_ : [10, 7] (128)
                                                                                                                                          IterEnd    : [10, 22] (143)
                                                                                                                                          Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [10, 7] (128)
                                                                                                                        IterEnd    : [10, 22] (143)
                                                                                                                        Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterBegin_ : [10, 23] (144)
                                                                                                                                                                              IterEnd    : [10, 26] (147)
                                                                                                                                                                              Type       : 'and' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(144, 147), match='and'>
                                                                                                                                                                              Whitespace : 0)   143
                                                                                                                                                                                           1)   144
                                                                                                                                                            IterBegin_ : [10, 23] (144)
                                                                                                                                                            IterEnd    : [10, 26] (147)
                                                                                                                                                            Type       : Or: ('and', 'or') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                IterBegin_ : [10, 27] (148)
                                                                                                                                                                                                IterEnd    : [10, 28] (149)
                                                                                                                                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(148, 149), match='('>
                                                                                                                                                                                                Whitespace : 0)   147
                                                                                                                                                                                                             1)   148
                                                                                                                                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                    IterBegin_ : [10, 28] (149)
                                                                                                                                                                                                                                    IterEnd    : [10, 36] (157)
                                                                                                                                                                                                                                    Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(149, 157), match='__syntax'>
                                                                                                                                                                                                                                    Whitespace : None
                                                                                                                                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                      IsIgnored  : False
                                                                                                                                                                                                                                                      IterBegin_ : [10, 37] (158)
                                                                                                                                                                                                                                                      IterEnd    : [10, 39] (160)
                                                                                                                                                                                                                                                      Type       : '!=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                   Match : <_sre.SRE_Match object; span=(158, 160), match='!='>
                                                                                                                                                                                                                                                      Whitespace : 0)   157
                                                                                                                                                                                                                                                                   1)   158
                                                                                                                                                                                                                                    IterBegin_ : [10, 37] (158)
                                                                                                                                                                                                                                    IterEnd    : [10, 39] (160)
                                                                                                                                                                                                                                    Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                    IterBegin_ : [10, 40] (161)
                                                                                                                                                                                                                                    IterEnd    : [10, 43] (164)
                                                                                                                                                                                                                                    Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(161, 164), match='2.0'>
                                                                                                                                                                                                                                    Whitespace : 0)   160
                                                                                                                                                                                                                                                 1)   161
                                                                                                                                                                                                                  IterBegin_ : [10, 28] (149)
                                                                                                                                                                                                                  IterEnd    : [10, 43] (164)
                                                                                                                                                                                                                  Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                IterBegin_ : [10, 28] (149)
                                                                                                                                                                                                IterEnd    : [10, 43] (164)
                                                                                                                                                                                                Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                      IsIgnored  : False
                                                                                                                                                                                                                                                      IterBegin_ : [10, 44] (165)
                                                                                                                                                                                                                                                      IterEnd    : [10, 46] (167)
                                                                                                                                                                                                                                                      Type       : 'or' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                   Match : <_sre.SRE_Match object; span=(165, 167), match='or'>
                                                                                                                                                                                                                                                      Whitespace : 0)   164
                                                                                                                                                                                                                                                                   1)   165
                                                                                                                                                                                                                                    IterBegin_ : [10, 44] (165)
                                                                                                                                                                                                                                    IterEnd    : [10, 46] (167)
                                                                                                                                                                                                                                    Type       : Or: ('and', 'or') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                        IsIgnored  : False
                                                                                                                                                                                                                                                                        IterBegin_ : [10, 47] (168)
                                                                                                                                                                                                                                                                        IterEnd    : [10, 55] (176)
                                                                                                                                                                                                                                                                        Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(168, 176), match='__syntax'>
                                                                                                                                                                                                                                                                        Whitespace : 0)   167
                                                                                                                                                                                                                                                                                     1)   168
                                                                                                                                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                                                                                                                                          IterBegin_ : [10, 56] (177)
                                                                                                                                                                                                                                                                                          IterEnd    : [10, 58] (179)
                                                                                                                                                                                                                                                                                          Type       : '!=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(177, 179), match='!='>
                                                                                                                                                                                                                                                                                          Whitespace : 0)   176
                                                                                                                                                                                                                                                                                                       1)   177
                                                                                                                                                                                                                                                                        IterBegin_ : [10, 56] (177)
                                                                                                                                                                                                                                                                        IterEnd    : [10, 58] (179)
                                                                                                                                                                                                                                                                        Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                        IsIgnored  : False
                                                                                                                                                                                                                                                                        IterBegin_ : [10, 59] (180)
                                                                                                                                                                                                                                                                        IterEnd    : [10, 62] (183)
                                                                                                                                                                                                                                                                        Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(180, 183), match='3.0'>
                                                                                                                                                                                                                                                                        Whitespace : 0)   179
                                                                                                                                                                                                                                                                                     1)   180
                                                                                                                                                                                                                                                      IterBegin_ : [10, 47] (168)
                                                                                                                                                                                                                                                      IterEnd    : [10, 62] (183)
                                                                                                                                                                                                                                                      Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                    IterBegin_ : [10, 47] (168)
                                                                                                                                                                                                                                    IterEnd    : [10, 62] (183)
                                                                                                                                                                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                  IterBegin_ : [10, 44] (165)
                                                                                                                                                                                                                  IterEnd    : [10, 62] (183)
                                                                                                                                                                                                                  Type       : Sequence: [Or: ('and', 'or'), Condition Phrase] <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                IterBegin_ : [10, 44] (165)
                                                                                                                                                                                                IterEnd    : [10, 62] (183)
                                                                                                                                                                                                Type       : Repeat: {Sequence: [Or: ('and', 'or'), Condition Phrase], 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                IterBegin_ : [10, 62] (183)
                                                                                                                                                                                                IterEnd    : [10, 63] (184)
                                                                                                                                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(183, 184), match=')'>
                                                                                                                                                                                                Whitespace : None
                                                                                                                                                                              IterBegin_ : [10, 27] (148)
                                                                                                                                                                              IterEnd    : [10, 63] (184)
                                                                                                                                                                              Type       : Logical <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                            IterBegin_ : [10, 27] (148)
                                                                                                                                                            IterEnd    : [10, 63] (184)
                                                                                                                                                            Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                          IterBegin_ : [10, 23] (144)
                                                                                                                                          IterEnd    : [10, 63] (184)
                                                                                                                                          Type       : Sequence: [Or: ('and', 'or'), Condition Phrase] <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [10, 23] (144)
                                                                                                                        IterEnd    : [10, 63] (184)
                                                                                                                        Type       : Repeat: {Sequence: [Or: ('and', 'or'), Condition Phrase], 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                   3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterBegin_ : [10, 63] (184)
                                                                                                                        IterEnd    : [10, 64] (185)
                                                                                                                        Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(184, 185), match=')'>
                                                                                                                        Whitespace : None
                                                                                                      IterBegin_ : [10, 6] (127)
                                                                                                      IterEnd    : [10, 64] (185)
                                                                                                      Type       : Logical <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                    IterBegin_ : [10, 6] (127)
                                                                                    IterEnd    : [10, 64] (185)
                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [10, 64] (185)
                                                                                    IterEnd    : [10, 65] (186)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(185, 186), match=':'>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [10, 65] (186)
                                                                                    IterEnd    : [11, 1] (187)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 187
                                                                                                 Start : 186
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [11, 1] (187)
                                                                                    IterEnd    : [11, 5] (191)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 191
                                                                                                 Start : 187
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [11, 5] (191)
                                                                                                                                                            IterEnd    : [11, 9] (195)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(191, 195), match='food'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [11, 9] (195)
                                                                                                                                                            IterEnd    : [12, 1] (196)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 196
                                                                                                                                                                         Start : 195
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [11, 5] (191)
                                                                                                                                          IterEnd    : [12, 1] (196)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [11, 5] (191)
                                                                                                                        IterEnd    : [12, 1] (196)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [11, 5] (191)
                                                                                                      IterEnd    : [12, 1] (196)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [12, 5] (200)
                                                                                                                                                            IterEnd    : [12, 9] (204)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(200, 204), match='fooe'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterBegin_ : [12, 9] (204)
                                                                                                                                                            IterEnd    : [13, 1] (205)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 205
                                                                                                                                                                         Start : 204
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterBegin_ : [12, 5] (200)
                                                                                                                                          IterEnd    : [13, 1] (205)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterBegin_ : [12, 5] (200)
                                                                                                                        IterEnd    : [13, 1] (205)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterBegin_ : [12, 5] (200)
                                                                                                      IterEnd    : [13, 1] (205)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterBegin_ : [11, 5] (191)
                                                                                    IterEnd    : [13, 1] (205)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterBegin_ : [13, 1] (205)
                                                                                    IterEnd    : [13, 1] (205)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterBegin_ : [10, 1] (122)
                                                                  IterEnd    : [13, 1] (205)
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterBegin_ : [10, 1] (122)
                                                IterEnd    : [13, 1] (205)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterBegin_ : [10, 1] (122)
                              IterEnd    : [13, 1] (205)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterBegin_ : [1, 1] (0)
            IterEnd    : [13, 1] (205)
            Type       : <None>
            """,
        )
