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
        SemVer("1.0.0") : DynamicPhrasesInfo((), (), (_upper_phrase, _lower_phrase), ()),
        SemVer("2.0.0") : DynamicPhrasesInfo((), (), (_upper_phrase, _lower_phrase, _number_phrase), ()),
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
                                                                                    IterAfter  : [1, 6] (5)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 5), match='UPPER'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (6)
                                                                                    IterBefore : [1, 6] (5)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 6
                                                                                                 Start : 5
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (6)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (6)
                                                IterBefore : [1, 1] (0)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (6)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 6] (11)
                                                                                    IterBefore : [2, 1] (6)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(6, 11), match='lower'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (12)
                                                                                    IterBefore : [2, 6] (11)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 12
                                                                                                 Start : 11
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (12)
                                                                  IterBefore : [2, 1] (6)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (12)
                                                IterBefore : [2, 1] (6)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (12)
                              IterBefore : [2, 1] (6)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 5] (16)
                                                                                    IterBefore : [3, 1] (12)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(12, 16), match='1234'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (17)
                                                                                    IterBefore : [3, 5] (16)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 17
                                                                                                 Start : 16
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (17)
                                                                  IterBefore : [3, 1] (12)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (17)
                                                IterBefore : [3, 1] (12)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (17)
                              IterBefore : [3, 1] (12)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (17)
            IterBefore : [1, 1] (0)
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
                                                                                    IterAfter  : [1, 7] (6)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 6), match='AUPPER'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (7)
                                                                                    IterBefore : [1, 7] (6)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 7
                                                                                                 Start : 6
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (7)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (7)
                                                IterBefore : [1, 1] (0)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (7)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 7] (13)
                                                                                    IterBefore : [2, 1] (7)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(7, 13), match='alower'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (14)
                                                                                    IterBefore : [2, 7] (13)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 14
                                                                                                 Start : 13
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (14)
                                                                  IterBefore : [2, 1] (7)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (14)
                                                IterBefore : [2, 1] (7)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (14)
                              IterBefore : [2, 1] (7)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 5] (18)
                                                                                    IterBefore : [3, 1] (14)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(14, 18), match='1234'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 1] (20)
                                                                                    IterBefore : [3, 5] (18)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 20
                                                                                                 Start : 18
                                                                                    Whitespace : None
                                                                  IterAfter  : [5, 1] (20)
                                                                  IterBefore : [3, 1] (14)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [5, 1] (20)
                                                IterBefore : [3, 1] (14)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [5, 1] (20)
                              IterBefore : [3, 1] (14)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 7] (26)
                                                                                    IterBefore : [5, 1] (20)
                                                                                    Type       : '__with' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(20, 26), match='__with'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 16] (35)
                                                                                    IterBefore : [5, 8] (27)
                                                                                    Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(27, 35), match='__syntax'>
                                                                                    Whitespace : 0)   26
                                                                                                 1)   27
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 17] (36)
                                                                                    IterBefore : [5, 16] (35)
                                                                                    Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(35, 36), match='='>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 20] (39)
                                                                                    IterBefore : [5, 17] (36)
                                                                                    Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(36, 39), match='1.0'>
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 21] (40)
                                                                                    IterBefore : [5, 20] (39)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(39, 40), match=':'>
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 1] (41)
                                                                                    IterBefore : [5, 21] (40)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 41
                                                                                                 Start : 40
                                                                                    Whitespace : None
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 5] (45)
                                                                                    IterBefore : [6, 1] (41)
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
                                                                                                                                                            IterAfter  : [6, 11] (51)
                                                                                                                                                            IterBefore : [6, 5] (45)
                                                                                                                                                            Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(45, 51), match='BUPPER'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [7, 1] (52)
                                                                                                                                                            IterBefore : [6, 11] (51)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 52
                                                                                                                                                                         Start : 51
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [7, 1] (52)
                                                                                                                                          IterBefore : [6, 5] (45)
                                                                                                                                          Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [7, 1] (52)
                                                                                                                        IterBefore : [6, 5] (45)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [7, 1] (52)
                                                                                                      IterBefore : [6, 5] (45)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [7, 11] (62)
                                                                                                                                                            IterBefore : [7, 5] (56)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(56, 62), match='blower'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [9, 1] (64)
                                                                                                                                                            IterBefore : [7, 11] (62)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 64
                                                                                                                                                                         Start : 62
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [9, 1] (64)
                                                                                                                                          IterBefore : [7, 5] (56)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [9, 1] (64)
                                                                                                                        IterBefore : [7, 5] (56)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [9, 1] (64)
                                                                                                      IterBefore : [7, 5] (56)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterAfter  : [9, 1] (64)
                                                                                    IterBefore : [6, 5] (45)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               8)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [9, 1] (64)
                                                                                    IterBefore : [9, 1] (64)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [9, 1] (64)
                                                                  IterBefore : [5, 1] (20)
                                                                  Type       : Set Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [9, 1] (64)
                                                IterBefore : [5, 1] (20)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [9, 1] (64)
                              IterBefore : [5, 1] (20)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [9, 7] (70)
                                                                                    IterBefore : [9, 1] (64)
                                                                                    Type       : '__with' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(64, 70), match='__with'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [9, 16] (79)
                                                                                    IterBefore : [9, 8] (71)
                                                                                    Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(71, 79), match='__syntax'>
                                                                                    Whitespace : 0)   70
                                                                                                 1)   71
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [9, 17] (80)
                                                                                    IterBefore : [9, 16] (79)
                                                                                    Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(79, 80), match='='>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [9, 22] (85)
                                                                                    IterBefore : [9, 17] (80)
                                                                                    Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(80, 85), match='1.0.0'>
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [9, 23] (86)
                                                                                    IterBefore : [9, 22] (85)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(85, 86), match=':'>
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [10, 1] (87)
                                                                                    IterBefore : [9, 23] (86)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 87
                                                                                                 Start : 86
                                                                                    Whitespace : None
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [10, 5] (91)
                                                                                    IterBefore : [10, 1] (87)
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
                                                                                                                                                            IterAfter  : [10, 11] (97)
                                                                                                                                                            IterBefore : [10, 5] (91)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(91, 97), match='clower'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [12, 1] (99)
                                                                                                                                                            IterBefore : [10, 11] (97)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 99
                                                                                                                                                                         Start : 97
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [12, 1] (99)
                                                                                                                                          IterBefore : [10, 5] (91)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [12, 1] (99)
                                                                                                                        IterBefore : [10, 5] (91)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [12, 1] (99)
                                                                                                      IterBefore : [10, 5] (91)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterAfter  : [12, 1] (99)
                                                                                    IterBefore : [10, 5] (91)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               8)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [12, 1] (99)
                                                                                    IterBefore : [12, 1] (99)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [12, 1] (99)
                                                                  IterBefore : [9, 1] (64)
                                                                  Type       : Set Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [12, 1] (99)
                                                IterBefore : [9, 1] (64)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [12, 1] (99)
                              IterBefore : [9, 1] (64)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [12, 7] (105)
                                                                                    IterBefore : [12, 1] (99)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(99, 105), match='456789'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [13, 1] (106)
                                                                                    IterBefore : [12, 7] (105)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 106
                                                                                                 Start : 105
                                                                                    Whitespace : None
                                                                  IterAfter  : [13, 1] (106)
                                                                  IterBefore : [12, 1] (99)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [13, 1] (106)
                                                IterBefore : [12, 1] (99)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [13, 1] (106)
                              IterBefore : [12, 1] (99)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [13, 1] (106)
            IterBefore : [1, 1] (0)
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
                                                                                    IterAfter  : [1, 7] (6)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 6), match='AUPPER'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (7)
                                                                                    IterBefore : [1, 7] (6)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 7
                                                                                                 Start : 6
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (7)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (7)
                                                IterBefore : [1, 1] (0)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (7)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 7] (13)
                                                                                    IterBefore : [2, 1] (7)
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(7, 13), match='alower'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (14)
                                                                                    IterBefore : [2, 7] (13)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 14
                                                                                                 Start : 13
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (14)
                                                                  IterBefore : [2, 1] (7)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (14)
                                                IterBefore : [2, 1] (7)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (14)
                              IterBefore : [2, 1] (7)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 5] (18)
                                                                                    IterBefore : [3, 1] (14)
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(14, 18), match='1234'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 1] (20)
                                                                                    IterBefore : [3, 5] (18)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 20
                                                                                                 Start : 18
                                                                                    Whitespace : None
                                                                  IterAfter  : [5, 1] (20)
                                                                  IterBefore : [3, 1] (14)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [5, 1] (20)
                                                IterBefore : [3, 1] (14)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [5, 1] (20)
                              IterBefore : [3, 1] (14)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 7] (26)
                                                                                    IterBefore : [5, 1] (20)
                                                                                    Type       : '__with' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(20, 26), match='__with'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 16] (35)
                                                                                    IterBefore : [5, 8] (27)
                                                                                    Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(27, 35), match='__syntax'>
                                                                                    Whitespace : 0)   26
                                                                                                 1)   27
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 17] (36)
                                                                                    IterBefore : [5, 16] (35)
                                                                                    Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(35, 36), match='='>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 20] (39)
                                                                                    IterBefore : [5, 17] (36)
                                                                                    Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(36, 39), match='1.0'>
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 21] (40)
                                                                                    IterBefore : [5, 20] (39)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(39, 40), match=':'>
                                                                                    Whitespace : None
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 1] (41)
                                                                                    IterBefore : [5, 21] (40)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 41
                                                                                                 Start : 40
                                                                                    Whitespace : None
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 5] (45)
                                                                                    IterBefore : [6, 1] (41)
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
                                                                                                                                                            IterAfter  : [6, 11] (51)
                                                                                                                                                            IterBefore : [6, 5] (45)
                                                                                                                                                            Type       : Upper Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(45, 51), match='BUPPER'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [7, 1] (52)
                                                                                                                                                            IterBefore : [6, 11] (51)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 52
                                                                                                                                                                         Start : 51
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [7, 1] (52)
                                                                                                                                          IterBefore : [6, 5] (45)
                                                                                                                                          Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [7, 1] (52)
                                                                                                                        IterBefore : [6, 5] (45)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [7, 1] (52)
                                                                                                      IterBefore : [6, 5] (45)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [7, 11] (62)
                                                                                                                                                            IterBefore : [7, 5] (56)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(56, 62), match='blower'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [8, 1] (63)
                                                                                                                                                            IterBefore : [7, 11] (62)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 63
                                                                                                                                                                         Start : 62
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [8, 1] (63)
                                                                                                                                          IterBefore : [7, 5] (56)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [8, 1] (63)
                                                                                                                        IterBefore : [7, 5] (56)
                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [8, 1] (63)
                                                                                                      IterBefore : [7, 5] (56)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterAfter  : [8, 1] (63)
                                                                                    IterBefore : [6, 5] (45)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : [5, 1] (20)
                                                                  Type       : Set Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Upper Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Lower Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Number Token <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : None
                                                IterBefore : None
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
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
                                                                                    IterAfter  : [1, 5] (4)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 4), match='__if'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [1, 14] (13)
                                                                                                                        IterBefore : [1, 6] (5)
                                                                                                                        Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(5, 13), match='__syntax'>
                                                                                                                        Whitespace : 0)   4
                                                                                                                                     1)   5
                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [1, 17] (16)
                                                                                                                                          IterBefore : [1, 15] (14)
                                                                                                                                          Type       : '==' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(14, 16), match='=='>
                                                                                                                                          Whitespace : 0)   13
                                                                                                                                                       1)   14
                                                                                                                        IterAfter  : [1, 17] (16)
                                                                                                                        IterBefore : [1, 15] (14)
                                                                                                                        Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [1, 23] (22)
                                                                                                                        IterBefore : [1, 18] (17)
                                                                                                                        Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(17, 22), match='1.2.3'>
                                                                                                                        Whitespace : 0)   16
                                                                                                                                     1)   17
                                                                                                      IterAfter  : [1, 23] (22)
                                                                                                      IterBefore : [1, 6] (5)
                                                                                                      Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                    IterAfter  : [1, 23] (22)
                                                                                    IterBefore : [1, 6] (5)
                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 24] (23)
                                                                                    IterBefore : [1, 23] (22)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(22, 23), match=':'>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (24)
                                                                                    IterBefore : [1, 24] (23)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 24
                                                                                                 Start : 23
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 5] (28)
                                                                                    IterBefore : [2, 1] (24)
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
                                                                                                                                                            IterAfter  : [2, 9] (32)
                                                                                                                                                            IterBefore : [2, 5] (28)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(28, 32), match='fooa'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [4, 1] (34)
                                                                                                                                                            IterBefore : [2, 9] (32)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 34
                                                                                                                                                                         Start : 32
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [4, 1] (34)
                                                                                                                                          IterBefore : [2, 5] (28)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [4, 1] (34)
                                                                                                                        IterBefore : [2, 5] (28)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [4, 1] (34)
                                                                                                      IterBefore : [2, 5] (28)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterAfter  : [4, 1] (34)
                                                                                    IterBefore : [2, 5] (28)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (34)
                                                                                    IterBefore : [4, 1] (34)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (34)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (34)
                                                IterBefore : [1, 1] (0)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (34)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 5] (38)
                                                                                    IterBefore : [4, 1] (34)
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(34, 38), match='__if'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [4, 9] (42)
                                                                                                                        IterBefore : [4, 6] (39)
                                                                                                                        Type       : 'not' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(39, 42), match='not'>
                                                                                                                        Whitespace : 0)   38
                                                                                                                                     1)   39
                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [4, 18] (51)
                                                                                                                                                            IterBefore : [4, 10] (43)
                                                                                                                                                            Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(43, 51), match='__syntax'>
                                                                                                                                                            Whitespace : 0)   42
                                                                                                                                                                         1)   43
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterAfter  : [4, 21] (54)
                                                                                                                                                                              IterBefore : [4, 19] (52)
                                                                                                                                                                              Type       : '==' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(52, 54), match='=='>
                                                                                                                                                                              Whitespace : 0)   51
                                                                                                                                                                                           1)   52
                                                                                                                                                            IterAfter  : [4, 21] (54)
                                                                                                                                                            IterBefore : [4, 19] (52)
                                                                                                                                                            Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [4, 25] (58)
                                                                                                                                                            IterBefore : [4, 22] (55)
                                                                                                                                                            Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(55, 58), match='4.0'>
                                                                                                                                                            Whitespace : 0)   54
                                                                                                                                                                         1)   55
                                                                                                                                          IterAfter  : [4, 25] (58)
                                                                                                                                          IterBefore : [4, 10] (43)
                                                                                                                                          Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [4, 25] (58)
                                                                                                                        IterBefore : [4, 10] (43)
                                                                                                                        Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [4, 25] (58)
                                                                                                      IterBefore : [4, 6] (39)
                                                                                                      Type       : Not <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                    IterAfter  : [4, 25] (58)
                                                                                    IterBefore : [4, 6] (39)
                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 26] (59)
                                                                                    IterBefore : [4, 25] (58)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(58, 59), match=':'>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 1] (60)
                                                                                    IterBefore : [4, 26] (59)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 60
                                                                                                 Start : 59
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 5] (64)
                                                                                    IterBefore : [5, 1] (60)
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
                                                                                                                                                            IterAfter  : [5, 9] (68)
                                                                                                                                                            IterBefore : [5, 5] (64)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(64, 68), match='foob'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [7, 1] (70)
                                                                                                                                                            IterBefore : [5, 9] (68)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 70
                                                                                                                                                                         Start : 68
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [7, 1] (70)
                                                                                                                                          IterBefore : [5, 5] (64)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [7, 1] (70)
                                                                                                                        IterBefore : [5, 5] (64)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [7, 1] (70)
                                                                                                      IterBefore : [5, 5] (64)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterAfter  : [7, 1] (70)
                                                                                    IterBefore : [5, 5] (64)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [7, 1] (70)
                                                                                    IterBefore : [7, 1] (70)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [7, 1] (70)
                                                                  IterBefore : [4, 1] (34)
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [7, 1] (70)
                                                IterBefore : [4, 1] (34)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [7, 1] (70)
                              IterBefore : [4, 1] (34)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [7, 5] (74)
                                                                                    IterBefore : [7, 1] (70)
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(70, 74), match='__if'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [7, 7] (76)
                                                                                                                        IterBefore : [7, 6] (75)
                                                                                                                        Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(75, 76), match='('>
                                                                                                                        Whitespace : 0)   74
                                                                                                                                     1)   75
                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [7, 15] (84)
                                                                                                                                                            IterBefore : [7, 7] (76)
                                                                                                                                                            Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(76, 84), match='__syntax'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterAfter  : [7, 17] (86)
                                                                                                                                                                              IterBefore : [7, 16] (85)
                                                                                                                                                                              Type       : '<' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(85, 86), match='<'>
                                                                                                                                                                              Whitespace : 0)   84
                                                                                                                                                                                           1)   85
                                                                                                                                                            IterAfter  : [7, 17] (86)
                                                                                                                                                            IterBefore : [7, 16] (85)
                                                                                                                                                            Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [7, 21] (90)
                                                                                                                                                            IterBefore : [7, 18] (87)
                                                                                                                                                            Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(87, 90), match='1.0'>
                                                                                                                                                            Whitespace : 0)   86
                                                                                                                                                                         1)   87
                                                                                                                                          IterAfter  : [7, 21] (90)
                                                                                                                                          IterBefore : [7, 7] (76)
                                                                                                                                          Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [7, 21] (90)
                                                                                                                        IterBefore : [7, 7] (76)
                                                                                                                        Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterAfter  : [7, 25] (94)
                                                                                                                                                                              IterBefore : [7, 22] (91)
                                                                                                                                                                              Type       : 'and' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(91, 94), match='and'>
                                                                                                                                                                              Whitespace : 0)   90
                                                                                                                                                                                           1)   91
                                                                                                                                                            IterAfter  : [7, 25] (94)
                                                                                                                                                            IterBefore : [7, 22] (91)
                                                                                                                                                            Type       : Or: ('and', 'or') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                IterAfter  : [7, 34] (103)
                                                                                                                                                                                                IterBefore : [7, 26] (95)
                                                                                                                                                                                                Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(95, 103), match='__syntax'>
                                                                                                                                                                                                Whitespace : 0)   94
                                                                                                                                                                                                             1)   95
                                                                                                                                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                  IsIgnored  : False
                                                                                                                                                                                                                  IterAfter  : [7, 36] (105)
                                                                                                                                                                                                                  IterBefore : [7, 35] (104)
                                                                                                                                                                                                                  Type       : '>' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                               Match : <_sre.SRE_Match object; span=(104, 105), match='>'>
                                                                                                                                                                                                                  Whitespace : 0)   103
                                                                                                                                                                                                                               1)   104
                                                                                                                                                                                                IterAfter  : [7, 36] (105)
                                                                                                                                                                                                IterBefore : [7, 35] (104)
                                                                                                                                                                                                Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                IterAfter  : [7, 40] (109)
                                                                                                                                                                                                IterBefore : [7, 37] (106)
                                                                                                                                                                                                Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(106, 109), match='2.0'>
                                                                                                                                                                                                Whitespace : 0)   105
                                                                                                                                                                                                             1)   106
                                                                                                                                                                              IterAfter  : [7, 40] (109)
                                                                                                                                                                              IterBefore : [7, 26] (95)
                                                                                                                                                                              Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                            IterAfter  : [7, 40] (109)
                                                                                                                                                            IterBefore : [7, 26] (95)
                                                                                                                                                            Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                          IterAfter  : [7, 40] (109)
                                                                                                                                          IterBefore : [7, 22] (91)
                                                                                                                                          Type       : Sequence: [Or: ('and', 'or'), Condition Phrase] <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [7, 40] (109)
                                                                                                                        IterBefore : [7, 22] (91)
                                                                                                                        Type       : Repeat: {Sequence: [Or: ('and', 'or'), Condition Phrase], 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                   3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [7, 41] (110)
                                                                                                                        IterBefore : [7, 40] (109)
                                                                                                                        Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(109, 110), match=')'>
                                                                                                                        Whitespace : None
                                                                                                      IterAfter  : [7, 41] (110)
                                                                                                      IterBefore : [7, 6] (75)
                                                                                                      Type       : Logical <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                    IterAfter  : [7, 41] (110)
                                                                                    IterBefore : [7, 6] (75)
                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [7, 42] (111)
                                                                                    IterBefore : [7, 41] (110)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(110, 111), match=':'>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [8, 1] (112)
                                                                                    IterBefore : [7, 42] (111)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 112
                                                                                                 Start : 111
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [8, 5] (116)
                                                                                    IterBefore : [8, 1] (112)
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
                                                                                                                                                            IterAfter  : [8, 9] (120)
                                                                                                                                                            IterBefore : [8, 5] (116)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(116, 120), match='fooc'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [10, 1] (122)
                                                                                                                                                            IterBefore : [8, 9] (120)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 122
                                                                                                                                                                         Start : 120
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [10, 1] (122)
                                                                                                                                          IterBefore : [8, 5] (116)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [10, 1] (122)
                                                                                                                        IterBefore : [8, 5] (116)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [10, 1] (122)
                                                                                                      IterBefore : [8, 5] (116)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterAfter  : [10, 1] (122)
                                                                                    IterBefore : [8, 5] (116)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [10, 1] (122)
                                                                                    IterBefore : [10, 1] (122)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [10, 1] (122)
                                                                  IterBefore : [7, 1] (70)
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [10, 1] (122)
                                                IterBefore : [7, 1] (70)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [10, 1] (122)
                              IterBefore : [7, 1] (70)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [10, 5] (126)
                                                                                    IterBefore : [10, 1] (122)
                                                                                    Type       : '__if' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(122, 126), match='__if'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [10, 7] (128)
                                                                                                                        IterBefore : [10, 6] (127)
                                                                                                                        Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(127, 128), match='('>
                                                                                                                        Whitespace : 0)   126
                                                                                                                                     1)   127
                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [10, 15] (136)
                                                                                                                                                            IterBefore : [10, 7] (128)
                                                                                                                                                            Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(128, 136), match='__syntax'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterAfter  : [10, 18] (139)
                                                                                                                                                                              IterBefore : [10, 16] (137)
                                                                                                                                                                              Type       : '!=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(137, 139), match='!='>
                                                                                                                                                                              Whitespace : 0)   136
                                                                                                                                                                                           1)   137
                                                                                                                                                            IterAfter  : [10, 18] (139)
                                                                                                                                                            IterBefore : [10, 16] (137)
                                                                                                                                                            Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [10, 22] (143)
                                                                                                                                                            IterBefore : [10, 19] (140)
                                                                                                                                                            Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(140, 143), match='2.0'>
                                                                                                                                                            Whitespace : 0)   139
                                                                                                                                                                         1)   140
                                                                                                                                          IterAfter  : [10, 22] (143)
                                                                                                                                          IterBefore : [10, 7] (128)
                                                                                                                                          Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [10, 22] (143)
                                                                                                                        IterBefore : [10, 7] (128)
                                                                                                                        Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                              IterAfter  : [10, 26] (147)
                                                                                                                                                                              IterBefore : [10, 23] (144)
                                                                                                                                                                              Type       : 'and' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(144, 147), match='and'>
                                                                                                                                                                              Whitespace : 0)   143
                                                                                                                                                                                           1)   144
                                                                                                                                                            IterAfter  : [10, 26] (147)
                                                                                                                                                            IterBefore : [10, 23] (144)
                                                                                                                                                            Type       : Or: ('and', 'or') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                IterAfter  : [10, 28] (149)
                                                                                                                                                                                                IterBefore : [10, 27] (148)
                                                                                                                                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(148, 149), match='('>
                                                                                                                                                                                                Whitespace : 0)   147
                                                                                                                                                                                                             1)   148
                                                                                                                                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                    IterAfter  : [10, 36] (157)
                                                                                                                                                                                                                                    IterBefore : [10, 28] (149)
                                                                                                                                                                                                                                    Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(149, 157), match='__syntax'>
                                                                                                                                                                                                                                    Whitespace : None
                                                                                                                                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                      IsIgnored  : False
                                                                                                                                                                                                                                                      IterAfter  : [10, 39] (160)
                                                                                                                                                                                                                                                      IterBefore : [10, 37] (158)
                                                                                                                                                                                                                                                      Type       : '!=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                   Match : <_sre.SRE_Match object; span=(158, 160), match='!='>
                                                                                                                                                                                                                                                      Whitespace : 0)   157
                                                                                                                                                                                                                                                                   1)   158
                                                                                                                                                                                                                                    IterAfter  : [10, 39] (160)
                                                                                                                                                                                                                                    IterBefore : [10, 37] (158)
                                                                                                                                                                                                                                    Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                    IterAfter  : [10, 43] (164)
                                                                                                                                                                                                                                    IterBefore : [10, 40] (161)
                                                                                                                                                                                                                                    Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(161, 164), match='2.0'>
                                                                                                                                                                                                                                    Whitespace : 0)   160
                                                                                                                                                                                                                                                 1)   161
                                                                                                                                                                                                                  IterAfter  : [10, 43] (164)
                                                                                                                                                                                                                  IterBefore : [10, 28] (149)
                                                                                                                                                                                                                  Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                IterAfter  : [10, 43] (164)
                                                                                                                                                                                                IterBefore : [10, 28] (149)
                                                                                                                                                                                                Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                      IsIgnored  : False
                                                                                                                                                                                                                                                      IterAfter  : [10, 46] (167)
                                                                                                                                                                                                                                                      IterBefore : [10, 44] (165)
                                                                                                                                                                                                                                                      Type       : 'or' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                   Match : <_sre.SRE_Match object; span=(165, 167), match='or'>
                                                                                                                                                                                                                                                      Whitespace : 0)   164
                                                                                                                                                                                                                                                                   1)   165
                                                                                                                                                                                                                                    IterAfter  : [10, 46] (167)
                                                                                                                                                                                                                                    IterBefore : [10, 44] (165)
                                                                                                                                                                                                                                    Type       : Or: ('and', 'or') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                        IsIgnored  : False
                                                                                                                                                                                                                                                                        IterAfter  : [10, 55] (176)
                                                                                                                                                                                                                                                                        IterBefore : [10, 47] (168)
                                                                                                                                                                                                                                                                        Type       : '__syntax' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(168, 176), match='__syntax'>
                                                                                                                                                                                                                                                                        Whitespace : 0)   167
                                                                                                                                                                                                                                                                                     1)   168
                                                                                                                                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                                                                                                                                          IterAfter  : [10, 58] (179)
                                                                                                                                                                                                                                                                                          IterBefore : [10, 56] (177)
                                                                                                                                                                                                                                                                                          Type       : '!=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(177, 179), match='!='>
                                                                                                                                                                                                                                                                                          Whitespace : 0)   176
                                                                                                                                                                                                                                                                                                       1)   177
                                                                                                                                                                                                                                                                        IterAfter  : [10, 58] (179)
                                                                                                                                                                                                                                                                        IterBefore : [10, 56] (177)
                                                                                                                                                                                                                                                                        Type       : Or: ('==', '!=', '<', '<=', '>', '>=') <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                        IsIgnored  : False
                                                                                                                                                                                                                                                                        IterAfter  : [10, 62] (183)
                                                                                                                                                                                                                                                                        IterBefore : [10, 59] (180)
                                                                                                                                                                                                                                                                        Type       : <semantic_version> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(180, 183), match='3.0'>
                                                                                                                                                                                                                                                                        Whitespace : 0)   179
                                                                                                                                                                                                                                                                                     1)   180
                                                                                                                                                                                                                                                      IterAfter  : [10, 62] (183)
                                                                                                                                                                                                                                                      IterBefore : [10, 47] (168)
                                                                                                                                                                                                                                                      Type       : Comparison <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                    IterAfter  : [10, 62] (183)
                                                                                                                                                                                                                                    IterBefore : [10, 47] (168)
                                                                                                                                                                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                  IterAfter  : [10, 62] (183)
                                                                                                                                                                                                                  IterBefore : [10, 44] (165)
                                                                                                                                                                                                                  Type       : Sequence: [Or: ('and', 'or'), Condition Phrase] <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                IterAfter  : [10, 62] (183)
                                                                                                                                                                                                IterBefore : [10, 44] (165)
                                                                                                                                                                                                Type       : Repeat: {Sequence: [Or: ('and', 'or'), Condition Phrase], 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                IterAfter  : [10, 63] (184)
                                                                                                                                                                                                IterBefore : [10, 62] (183)
                                                                                                                                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(183, 184), match=')'>
                                                                                                                                                                                                Whitespace : None
                                                                                                                                                                              IterAfter  : [10, 63] (184)
                                                                                                                                                                              IterBefore : [10, 27] (148)
                                                                                                                                                                              Type       : Logical <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                            IterAfter  : [10, 63] (184)
                                                                                                                                                            IterBefore : [10, 27] (148)
                                                                                                                                                            Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                          IterAfter  : [10, 63] (184)
                                                                                                                                          IterBefore : [10, 23] (144)
                                                                                                                                          Type       : Sequence: [Or: ('and', 'or'), Condition Phrase] <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [10, 63] (184)
                                                                                                                        IterBefore : [10, 23] (144)
                                                                                                                        Type       : Repeat: {Sequence: [Or: ('and', 'or'), Condition Phrase], 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                   3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [10, 64] (185)
                                                                                                                        IterBefore : [10, 63] (184)
                                                                                                                        Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(184, 185), match=')'>
                                                                                                                        Whitespace : None
                                                                                                      IterAfter  : [10, 64] (185)
                                                                                                      IterBefore : [10, 6] (127)
                                                                                                      Type       : Logical <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                    IterAfter  : [10, 64] (185)
                                                                                    IterBefore : [10, 6] (127)
                                                                                    Type       : Condition Phrase <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [10, 65] (186)
                                                                                    IterBefore : [10, 64] (185)
                                                                                    Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(185, 186), match=':'>
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [11, 1] (187)
                                                                                    IterBefore : [10, 65] (186)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 187
                                                                                                 Start : 186
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [11, 5] (191)
                                                                                    IterBefore : [11, 1] (187)
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
                                                                                                                                                            IterAfter  : [11, 9] (195)
                                                                                                                                                            IterBefore : [11, 5] (191)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(191, 195), match='food'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [12, 1] (196)
                                                                                                                                                            IterBefore : [11, 9] (195)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 196
                                                                                                                                                                         Start : 195
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [12, 1] (196)
                                                                                                                                          IterBefore : [11, 5] (191)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [12, 1] (196)
                                                                                                                        IterBefore : [11, 5] (191)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [12, 1] (196)
                                                                                                      IterBefore : [11, 5] (191)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [12, 9] (204)
                                                                                                                                                            IterBefore : [12, 5] (200)
                                                                                                                                                            Type       : Lower Token <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(200, 204), match='fooe'>
                                                                                                                                                            Whitespace : None
                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                            IsIgnored  : False
                                                                                                                                                            IterAfter  : [13, 1] (205)
                                                                                                                                                            IterBefore : [12, 9] (204)
                                                                                                                                                            Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                         End   : 205
                                                                                                                                                                         Start : 204
                                                                                                                                                            Whitespace : None
                                                                                                                                          IterAfter  : [13, 1] (205)
                                                                                                                                          IterBefore : [12, 5] (200)
                                                                                                                                          Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                        IterAfter  : [13, 1] (205)
                                                                                                                        IterBefore : [12, 5] (200)
                                                                                                                        Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                      IterAfter  : [13, 1] (205)
                                                                                                      IterBefore : [12, 5] (200)
                                                                                                      Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                    IterAfter  : [13, 1] (205)
                                                                                    IterBefore : [11, 5] (191)
                                                                                    Type       : Repeat: {DynamicPhrasesType.Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [13, 1] (205)
                                                                                    IterBefore : [13, 1] (205)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [13, 1] (205)
                                                                  IterBefore : [10, 1] (122)
                                                                  Type       : If Syntax <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [13, 1] (205)
                                                IterBefore : [10, 1] (122)
                                                Type       : 2.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [13, 1] (205)
                              IterBefore : [10, 1] (122)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [13, 1] (205)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )
