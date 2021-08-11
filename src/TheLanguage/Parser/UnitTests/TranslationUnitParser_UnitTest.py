# ----------------------------------------------------------------------
# |
# |  TranslationUnitParser_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-01 15:39:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for TranslationUnit.py"""

import os
import re
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TranslationUnitParser import *

    from ..Components.AST import Node

    from ..Components.Token import (
        DedentToken,
        IndentToken,
        NewlineToken,
        RegexToken,
    )

    from ..Components.UnitTests import (
        CoroutineMock,
        CreateIterator,
        MethodCallsToString,
        parse_mock as parse_mock_impl,
    )

    from ..Phrases.DSL import CreatePhrase, DynamicPhrasesType, PhraseItem


# ----------------------------------------------------------------------
@pytest.fixture
def parse_mock(parse_mock_impl):
    parse_mock_impl.OnPhraseCompleteAsync = CoroutineMock()

    return parse_mock_impl

# ----------------------------------------------------------------------
_upper_token                                = RegexToken("Upper", re.compile(r"(?P<value>[A-Z]+)"))
_lower_token                                = RegexToken("Lower", re.compile(r"(?P<value>[a-z]+)"))
_number_token                               = RegexToken("Number", re.compile(r"(?P<value>\d+)"))

# ----------------------------------------------------------------------
class TestSimple(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number Phrase", item=[_number_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo(
        (),
        (),
        (_upper_phrase, _lower_phrase, _number_phrase),
        (),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchStandard(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                    two
                    33333
                    """,
                ),
            ),
            parse_mock,
            single_threaded=True,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
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
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
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
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
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
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 6] (13)
                                                                                    IterBefore : [3, 1] (8)
                                                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 13), match='33333'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (14)
                                                                                    IterBefore : [3, 6] (13)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 14
                                                                                                 Start : 13
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (14)
                                                                  IterBefore : [3, 1] (8)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (14)
                                                IterBefore : [3, 1] (8)
                                                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (14)
                              IterBefore : [3, 1] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (14)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert MethodCallsToString(parse_mock) == textwrap.dedent(
            """\
            0) OnPhraseCompleteAsync, Upper, 0, 3
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [1, 4] (3)
                IterBefore : [1, 1] (0)
                Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
                Whitespace : None
            1) OnPhraseCompleteAsync, Newline+, 3, 4
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 4] (3)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 4
                             Start : 3
                Whitespace : None
            2) OnPhraseCompleteAsync, Upper Phrase, 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [1, 4] (3)
                                  IterBefore : [1, 1] (0)
                                  Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
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
                Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            3) OnPhraseCompleteAsync, (Upper Phrase, Lower Phrase, Number Phrase), 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [1, 4] (3)
                                                    IterBefore : [1, 1] (0)
                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
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
                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            4) OnPhraseCompleteAsync, Dynamic Phrases, 0, 4
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [1, 4] (3)
                                                                      IterBefore : [1, 1] (0)
                                                                      Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
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
                                                    Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [2, 1] (4)
                                  IterBefore : [1, 1] (0)
                                  Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [2, 1] (4)
                IterBefore : [1, 1] (0)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            5) OnPhraseCompleteAsync, Lower, 4, 7
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [2, 4] (7)
                IterBefore : [2, 1] (4)
                Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
                Whitespace : None
            6) OnPhraseCompleteAsync, Newline+, 7, 8
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 4] (7)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 8
                             Start : 7
                Whitespace : None
            7) OnPhraseCompleteAsync, Lower Phrase, 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [2, 4] (7)
                                  IterBefore : [2, 1] (4)
                                  Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
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
                Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            8) OnPhraseCompleteAsync, (Upper Phrase, Lower Phrase, Number Phrase), 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [2, 4] (7)
                                                    IterBefore : [2, 1] (4)
                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
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
                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            9) OnPhraseCompleteAsync, Dynamic Phrases, 4, 8
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [2, 4] (7)
                                                                      IterBefore : [2, 1] (4)
                                                                      Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
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
                                                    Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [3, 1] (8)
                                  IterBefore : [2, 1] (4)
                                  Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [3, 1] (8)
                IterBefore : [2, 1] (4)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            10) OnPhraseCompleteAsync, Number, 8, 13
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [3, 6] (13)
                IterBefore : [3, 1] (8)
                Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                             Match : <_sre.SRE_Match object; span=(8, 13), match='33333'>
                Whitespace : None
            11) OnPhraseCompleteAsync, Newline+, 13, 14
                <class 'TheLanguage.Parser.Components.AST.Leaf'>
                IsIgnored  : False
                IterAfter  : [4, 1] (14)
                IterBefore : [3, 6] (13)
                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                             End   : 14
                             Start : 13
                Whitespace : None
            12) OnPhraseCompleteAsync, Number Phrase, 8, 14
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [3, 6] (13)
                                  IterBefore : [3, 1] (8)
                                  Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                               Match : <_sre.SRE_Match object; span=(8, 13), match='33333'>
                                  Whitespace : None
                             1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                  IsIgnored  : False
                                  IterAfter  : [4, 1] (14)
                                  IterBefore : [3, 6] (13)
                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                               End   : 14
                                               Start : 13
                                  Whitespace : None
                IterAfter  : [4, 1] (14)
                IterBefore : [3, 1] (8)
                Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
            13) OnPhraseCompleteAsync, (Upper Phrase, Lower Phrase, Number Phrase), 8, 14
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [3, 6] (13)
                                                    IterBefore : [3, 1] (8)
                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                 Match : <_sre.SRE_Match object; span=(8, 13), match='33333'>
                                                    Whitespace : None
                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                    IsIgnored  : False
                                                    IterAfter  : [4, 1] (14)
                                                    IterBefore : [3, 6] (13)
                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                 End   : 14
                                                                 Start : 13
                                                    Whitespace : None
                                  IterAfter  : [4, 1] (14)
                                  IterBefore : [3, 1] (8)
                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                IterAfter  : [4, 1] (14)
                IterBefore : [3, 1] (8)
                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
            14) OnPhraseCompleteAsync, Dynamic Phrases, 8, 14
                <class 'TheLanguage.Parser.Components.AST.Node'>
                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [3, 6] (13)
                                                                      IterBefore : [3, 1] (8)
                                                                      Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                   Match : <_sre.SRE_Match object; span=(8, 13), match='33333'>
                                                                      Whitespace : None
                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                      IsIgnored  : False
                                                                      IterAfter  : [4, 1] (14)
                                                                      IterBefore : [3, 6] (13)
                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                   End   : 14
                                                                                   Start : 13
                                                                      Whitespace : None
                                                    IterAfter  : [4, 1] (14)
                                                    IterBefore : [3, 1] (8)
                                                    Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                  IterAfter  : [4, 1] (14)
                                  IterBefore : [3, 1] (8)
                                  Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                IterAfter  : [4, 1] (14)
                IterBefore : [3, 1] (8)
                Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            """,
        )


    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_MatchReverse(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    33
                    twooooooooo
                    ONE
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 3] (2)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 2), match='33'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (3)
                                                                                    IterBefore : [1, 3] (2)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 3
                                                                                                 Start : 2
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (3)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (3)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (3)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 12] (14)
                                                                                    IterBefore : [2, 1] (3)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(3, 14), match='twooooooooo'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (15)
                                                                                    IterBefore : [2, 12] (14)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 15
                                                                                                 Start : 14
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (15)
                                                                  IterBefore : [2, 1] (3)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (15)
                                                IterBefore : [2, 1] (3)
                                                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (15)
                              IterBefore : [2, 1] (3)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 4] (18)
                                                                                    IterBefore : [3, 1] (15)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(15, 18), match='ONE'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (19)
                                                                                    IterBefore : [3, 4] (18)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 19
                                                                                                 Start : 18
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (19)
                                                                  IterBefore : [3, 1] (15)
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (19)
                                                IterBefore : [3, 1] (15)
                                                Type       : (Upper Phrase, Lower Phrase, Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (19)
                              IterBefore : [3, 1] (15)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (19)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert len(parse_mock.method_calls) == 15

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_EarlyTermination(self, parse_mock):
        parse_mock.OnPhraseCompleteAsync = CoroutineMock(
            side_effect=[True, False],
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    33
                    twooooooooo
                    ONE
                    """,
                ),
            ),
            parse_mock,
        )

        assert result is None

# ----------------------------------------------------------------------
class TestIndentation(object):
    _phrase                                 = CreatePhrase(
        name="Phrase",
        item=[
            _upper_token,
            NewlineToken(),
            IndentToken(),
            _upper_token,
            _upper_token,
            NewlineToken(),
            DedentToken(),
        ],
    )

    _phrases                                = DynamicPhrasesInfo(
        (),
        (),
        (_phrase,),
        (),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        TWO      THREE
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
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
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 5] (8)
                                                                                    IterBefore : [2, 1] (4)
                                                                                    Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                                 End   : 8
                                                                                                 Start : 4
                                                                                                 Value : 4
                                                                                    Whitespace : None
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 8] (11)
                                                                                    IterBefore : [2, 5] (8)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 11), match='TWO'>
                                                                                    Whitespace : None
                                                                               4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 19] (22)
                                                                                    IterBefore : [2, 14] (17)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(17, 22), match='THREE'>
                                                                                    Whitespace : 0)   11
                                                                                                 1)   17
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (23)
                                                                                    IterBefore : [2, 19] (22)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 23
                                                                                                 Start : 22
                                                                                    Whitespace : None
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (23)
                                                                                    IterBefore : [3, 1] (23)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (23)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (23)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (23)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [3, 1] (23)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

# ----------------------------------------------------------------------
class TestNewPhrases(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=_upper_token)
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo((), (), (_upper_phrase,), ())
    _new_phrases                            = DynamicPhrasesInfo((), (), (_lower_phrase,), ())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnPhraseCompleteAsync = CoroutineMock(
            side_effect=[self._new_phrases, True, True, True, True, True, True, True, True],
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE two
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [1, 4] (3)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                               Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
                                                                  Whitespace : None
                                                IterAfter  : [1, 4] (3)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [1, 4] (3)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 8] (7)
                                                                                    IterBefore : [1, 5] (4)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
                                                                                    Whitespace : 0)   3
                                                                                                 1)   4
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (8)
                                                                                    IterBefore : [1, 8] (7)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 8
                                                                                                 Start : 7
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (8)
                                                                  IterBefore : [1, 5] (4)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (8)
                                                IterBefore : [1, 5] (4)
                                                Type       : (Upper Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (8)
                              IterBefore : [1, 5] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [2, 1] (8)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
                self._phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE two
                        """,
                    ),
                ),
                parse_mock,
            )

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 1
        assert ex.Column == 4

        assert ex.ToDebugString() == textwrap.dedent(
            """\
            The syntax is not recognized [1, 4]

            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [1, 4] (3)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                               Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
                                                                  Whitespace : None
                                                IterAfter  : [1, 4] (3)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [1, 4] (3)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : -- empty list --
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                IterAfter  : None
                                                IterBefore : None
                                                Type       : (Upper Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : None
                              IterBefore : None
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : None
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

# ----------------------------------------------------------------------
class TestNewScopedPhrases(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=_upper_token)
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=_lower_token)

    _newline_phrase                         = CreatePhrase(name="Newline Phrase", item=NewlineToken())
    _indent_phrase                          = CreatePhrase(name="Indent Phrase", item=IndentToken())
    _dedent_phrase                          = CreatePhrase(name="Dedent Phrase", item=DedentToken())

    _phrases                                = DynamicPhrasesInfo((), (), (_upper_phrase, _newline_phrase, _indent_phrase, _dedent_phrase), ())
    _new_phrases                            = DynamicPhrasesInfo((), (), (_lower_phrase,), ())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        two
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [1, 4] (3)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                               Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
                                                                  Whitespace : None
                                                IterAfter  : [1, 4] (3)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [1, 4] (3)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [2, 1] (4)
                                                                  IterBefore : [1, 4] (3)
                                                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                               End   : 4
                                                                               Start : 3
                                                                  Whitespace : None
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 4] (3)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 4] (3)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [2, 5] (8)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                               End   : 8
                                                                               Start : 4
                                                                               Value : 4
                                                                  Whitespace : None
                                                IterAfter  : [2, 5] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 5] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [2, 8] (11)
                                                                  IterBefore : [2, 5] (8)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                               Match : <_sre.SRE_Match object; span=(8, 11), match='two'>
                                                                  Whitespace : None
                                                IterAfter  : [2, 8] (11)
                                                IterBefore : [2, 5] (8)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 8] (11)
                              IterBefore : [2, 5] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [3, 1] (12)
                                                                  IterBefore : [2, 8] (11)
                                                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                               End   : 12
                                                                               Start : 11
                                                                  Whitespace : None
                                                IterAfter  : [3, 1] (12)
                                                IterBefore : [2, 8] (11)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (12)
                              IterBefore : [2, 8] (11)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [3, 1] (12)
                                                                  IterBefore : [3, 1] (12)
                                                                  Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                               -- empty dict --
                                                                  Whitespace : None
                                                IterAfter  : [3, 1] (12)
                                                IterBefore : [3, 1] (12)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (12)
                              IterBefore : [3, 1] (12)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [3, 1] (12)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
                self._phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE
                            two

                        nomatch
                        """,
                    ),
                ),
                parse_mock,
            )

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 4
        assert ex.Column == 1

        assert ex.ToDebugString() == textwrap.dedent(
            """\
            The syntax is not recognized [4, 1]

            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [1, 4] (3)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                               Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
                                                                  Whitespace : None
                                                IterAfter  : [1, 4] (3)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [1, 4] (3)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [2, 1] (4)
                                                                  IterBefore : [1, 4] (3)
                                                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                               End   : 4
                                                                               Start : 3
                                                                  Whitespace : None
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 4] (3)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 4] (3)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [2, 5] (8)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                               End   : 8
                                                                               Start : 4
                                                                               Value : 4
                                                                  Whitespace : None
                                                IterAfter  : [2, 5] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 5] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [2, 8] (11)
                                                                  IterBefore : [2, 5] (8)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                               Match : <_sre.SRE_Match object; span=(8, 11), match='two'>
                                                                  Whitespace : None
                                                IterAfter  : [2, 8] (11)
                                                IterBefore : [2, 5] (8)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 8] (11)
                              IterBefore : [2, 5] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [4, 1] (13)
                                                                  IterBefore : [2, 8] (11)
                                                                  Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                               End   : 13
                                                                               Start : 11
                                                                  Whitespace : None
                                                IterAfter  : [4, 1] (13)
                                                IterBefore : [2, 8] (11)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (13)
                              IterBefore : [2, 8] (11)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [4, 1] (13)
                                                                  IterBefore : [4, 1] (13)
                                                                  Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                               -- empty dict --
                                                                  Whitespace : None
                                                IterAfter  : [4, 1] (13)
                                                IterBefore : [4, 1] (13)
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (13)
                              IterBefore : [4, 1] (13)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         6)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : -- empty list --
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                             1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : -- empty list --
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Newline Phrase <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                             2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : -- empty list --
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Indent Phrase <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                             3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : -- empty list --
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Dedent Phrase <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                IterAfter  : None
                                                IterBefore : None
                                                Type       : (Upper Phrase, Newline Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : None
                              IterBefore : None
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : None
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

# ----------------------------------------------------------------------
class TestNewScopedPhrasesComplex(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=_upper_token)
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=_lower_token)

    _newline_phrase                         = CreatePhrase(name="Newline Phrase", item=NewlineToken())
    _dedent_phrase                          = CreatePhrase(name="Dedent Phrase", item=DedentToken())

    _new_scope_phrase                       = CreatePhrase(
        name="New Scope",
        item=[
            _upper_token,
            RegexToken("Colon", re.compile(r":")),
            NewlineToken(),
            IndentToken(),
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DedentToken(),
        ],
    )

    _phrases                             = DynamicPhrasesInfo((), (), (_newline_phrase, _new_scope_phrase), ())
    _new_phrases                         = DynamicPhrasesInfo((), (), (_upper_phrase, _lower_phrase), ())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=self._new_phrases,
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    NEWSCOPE:
                        UPPER

                        lower
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 9] (8)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 8), match='NEWSCOPE'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 10] (9)
                                                                                    IterBefore : [1, 9] (8)
                                                                                    Type       : Colon <class 'TheLanguage.Parser.Components.Token.RegexToken'>
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
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [2, 10] (19)
                                                                                                                        IterBefore : [2, 5] (14)
                                                                                                                        Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(14, 19), match='UPPER'>
                                                                                                                        Whitespace : None
                                                                                                      IterAfter  : [2, 10] (19)
                                                                                                      IterBefore : [2, 5] (14)
                                                                                                      Type       : (Newline Phrase, New Scope) / (Upper Phrase, Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [2, 10] (19)
                                                                                    IterBefore : [2, 5] (14)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [4, 1] (21)
                                                                                                                        IterBefore : [2, 10] (19)
                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                     End   : 21
                                                                                                                                     Start : 19
                                                                                                                        Whitespace : None
                                                                                                      IterAfter  : [4, 1] (21)
                                                                                                      IterBefore : [2, 10] (19)
                                                                                                      Type       : (Newline Phrase, New Scope) / (Upper Phrase, Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [4, 1] (21)
                                                                                    IterBefore : [2, 10] (19)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               6)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [4, 10] (30)
                                                                                                                        IterBefore : [4, 5] (25)
                                                                                                                        Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                     Match : <_sre.SRE_Match object; span=(25, 30), match='lower'>
                                                                                                                        Whitespace : None
                                                                                                      IterAfter  : [4, 10] (30)
                                                                                                      IterBefore : [4, 5] (25)
                                                                                                      Type       : (Newline Phrase, New Scope) / (Upper Phrase, Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [4, 10] (30)
                                                                                    IterBefore : [4, 5] (25)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               7)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                        IsIgnored  : False
                                                                                                                        IterAfter  : [5, 1] (31)
                                                                                                                        IterBefore : [4, 10] (30)
                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                     End   : 31
                                                                                                                                     Start : 30
                                                                                                                        Whitespace : None
                                                                                                      IterAfter  : [5, 1] (31)
                                                                                                      IterBefore : [4, 10] (30)
                                                                                                      Type       : (Newline Phrase, New Scope) / (Upper Phrase, Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [5, 1] (31)
                                                                                    IterBefore : [4, 10] (30)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               8)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [5, 1] (31)
                                                                                    IterBefore : [5, 1] (31)
                                                                                    Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                                 -- empty dict --
                                                                                    Whitespace : None
                                                                  IterAfter  : [5, 1] (31)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : New Scope <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [5, 1] (31)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Newline Phrase, New Scope) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [5, 1] (31)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [5, 1] (31)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

# ----------------------------------------------------------------------
class TestEmbeddedPhrases(object):
    _upper_lower_phrase                     = CreatePhrase(name="Upper Lower Phrase", item=[_upper_token, _lower_token, NewlineToken()])

    _uul_phrase                             = CreatePhrase(name="uul", item=[_upper_token, _upper_lower_phrase])
    _lul_phrase                             = CreatePhrase(name="lul", item=[_lower_token, _upper_lower_phrase])

    _phrases                                = DynamicPhrasesInfo((), (), (_uul_phrase, _lul_phrase), ())

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE TWO  three
                    four    FIVE six
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 8] (7)
                                                                                                      IterBefore : [1, 5] (4)
                                                                                                      Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(4, 7), match='TWO'>
                                                                                                      Whitespace : 0)   3
                                                                                                                   1)   4
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 15] (14)
                                                                                                      IterBefore : [1, 10] (9)
                                                                                                      Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(9, 14), match='three'>
                                                                                                      Whitespace : 0)   7
                                                                                                                   1)   9
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
                                                                                    IterBefore : [1, 5] (4)
                                                                                    Type       : Upper Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                  IterAfter  : [2, 1] (15)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : uul <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (15)
                                                IterBefore : [1, 1] (0)
                                                Type       : (uul, lul) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (15)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 5] (19)
                                                                                    IterBefore : [2, 1] (15)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(15, 19), match='four'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [2, 13] (27)
                                                                                                      IterBefore : [2, 9] (23)
                                                                                                      Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(23, 27), match='FIVE'>
                                                                                                      Whitespace : 0)   19
                                                                                                                   1)   23
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [2, 17] (31)
                                                                                                      IterBefore : [2, 14] (28)
                                                                                                      Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(28, 31), match='six'>
                                                                                                      Whitespace : 0)   27
                                                                                                                   1)   28
                                                                                                 2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [3, 1] (32)
                                                                                                      IterBefore : [2, 17] (31)
                                                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                   End   : 32
                                                                                                                   Start : 31
                                                                                                      Whitespace : None
                                                                                    IterAfter  : [3, 1] (32)
                                                                                    IterBefore : [2, 9] (23)
                                                                                    Type       : Upper Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                  IterAfter  : [3, 1] (32)
                                                                  IterBefore : [2, 1] (15)
                                                                  Type       : lul <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (32)
                                                IterBefore : [2, 1] (15)
                                                Type       : (uul, lul) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (32)
                              IterBefore : [2, 1] (15)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [3, 1] (32)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

# ----------------------------------------------------------------------
class TestVariedLengthMatches(object):
    _upper_phrase                           = CreatePhrase(name="Upper", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower", item=[_lower_token, _lower_token, NewlineToken()])
    _number_phrase                          = CreatePhrase(name="Number", item=[_number_token, _number_token, _number_token, NewlineToken()])

    _phrases                                = DynamicPhrasesInfo(
        (),
        (),
        (_upper_phrase, _lower_phrase, _number_phrase),
        (),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Match(self, parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    one two
                    1 2 3
                    WORD
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 8] (7)
                                                                                    IterBefore : [1, 5] (4)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(4, 7), match='two'>
                                                                                    Whitespace : 0)   3
                                                                                                 1)   4
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 1] (8)
                                                                                    IterBefore : [1, 8] (7)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 8
                                                                                                 Start : 7
                                                                                    Whitespace : None
                                                                  IterAfter  : [2, 1] (8)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Lower <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (8)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper, Lower, Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (8)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 2] (9)
                                                                                    IterBefore : [2, 1] (8)
                                                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 9), match='1'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 4] (11)
                                                                                    IterBefore : [2, 3] (10)
                                                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(10, 11), match='2'>
                                                                                    Whitespace : 0)   9
                                                                                                 1)   10
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 6] (13)
                                                                                    IterBefore : [2, 5] (12)
                                                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(12, 13), match='3'>
                                                                                    Whitespace : 0)   11
                                                                                                 1)   12
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (14)
                                                                                    IterBefore : [2, 6] (13)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 14
                                                                                                 Start : 13
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (14)
                                                                  IterBefore : [2, 1] (8)
                                                                  Type       : Number <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (14)
                                                IterBefore : [2, 1] (8)
                                                Type       : (Upper, Lower, Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (14)
                              IterBefore : [2, 1] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 5] (18)
                                                                                    IterBefore : [3, 1] (14)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(14, 18), match='WORD'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (19)
                                                                                    IterBefore : [3, 5] (18)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 19
                                                                                                 Start : 18
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (19)
                                                                  IterBefore : [3, 1] (14)
                                                                  Type       : Upper <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (19)
                                                IterBefore : [3, 1] (14)
                                                Type       : (Upper, Lower, Number) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (19)
                              IterBefore : [3, 1] (14)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (19)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_EmptyDynamicPhrasesInfo(parse_mock):
    parse_mock.OnPhraseCompleteAsync = CoroutineMock(
        return_value=DynamicPhrasesInfo((), (), (), ()),
    )

    result = await ParseAsync(
        DynamicPhrasesInfo(
            (),
            (),
            (
                CreatePhrase(name="Newline Phrase", item=NewlineToken()),
                CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()]),
            ),
            (),
        ),
        CreateIterator(
            textwrap.dedent(
                """\

                word
                """,
            ),
        ),
        parse_mock,
    )

    assert str(result) == textwrap.dedent(
        """\
        <class 'TheLanguage.Parser.Components.AST.RootNode'>
        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                              IsIgnored  : False
                                                              IterAfter  : [2, 1] (1)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                              Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                           End   : 1
                                                                           Start : 0
                                                              Whitespace : None
                                            IterAfter  : [2, 1] (1)
                                            IterBefore : [1, 1] (0)
                                            Type       : (Newline Phrase, Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (1)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 5] (5)
                                                                                IterBefore : [2, 1] (1)
                                                                                Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(1, 5), match='word'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [3, 1] (6)
                                                                                IterBefore : [2, 5] (5)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 6
                                                                                             Start : 5
                                                                                Whitespace : None
                                                              IterAfter  : [3, 1] (6)
                                                              IterBefore : [2, 1] (1)
                                                              Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [3, 1] (6)
                                            IterBefore : [2, 1] (1)
                                            Type       : (Newline Phrase, Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [3, 1] (6)
                          IterBefore : [2, 1] (1)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [3, 1] (6)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
class TestPreventParentTraversal(object):
    _upper_phrase                           = CreatePhrase(name="Upper Phrase", item=[_upper_token, NewlineToken()])
    _lower_phrase                           = CreatePhrase(name="Lower Phrase", item=[_lower_token, NewlineToken()])
    _indent_phrase                          = CreatePhrase(name="Indent Phrase", item=IndentToken())
    _dedent_phrase                          = CreatePhrase(name="Dedent Phrase", item=DedentToken())

    _phrases                                = DynamicPhrasesInfo(
        (),
        (),
        (_upper_phrase, _indent_phrase, _dedent_phrase),
        (),
    )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async  def test_Match(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=DynamicPhrasesInfo(
                (),
                (),
                (self._lower_phrase, self._dedent_phrase),
                (),
                False,
            ),
        )

        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    ONE
                        two
                        three
                        four

                    FIVE
                    """,
                ),
            ),
            parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
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
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [2, 5] (8)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                               End   : 8
                                                                               Start : 4
                                                                               Value : 4
                                                                  Whitespace : None
                                                IterAfter  : [2, 5] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Upper Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 5] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 8] (11)
                                                                                    IterBefore : [2, 5] (8)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 11), match='two'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (12)
                                                                                    IterBefore : [2, 8] (11)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 12
                                                                                                 Start : 11
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (12)
                                                                  IterBefore : [2, 5] (8)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (12)
                                                IterBefore : [2, 5] (8)
                                                Type       : (Lower Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (12)
                              IterBefore : [2, 5] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 10] (21)
                                                                                    IterBefore : [3, 5] (16)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(16, 21), match='three'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (22)
                                                                                    IterBefore : [3, 10] (21)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 22
                                                                                                 Start : 21
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (22)
                                                                  IterBefore : [3, 5] (16)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (22)
                                                IterBefore : [3, 5] (16)
                                                Type       : (Lower Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (22)
                              IterBefore : [3, 5] (16)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 9] (30)
                                                                                    IterBefore : [4, 5] (26)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(26, 30), match='four'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 1] (32)
                                                                                    IterBefore : [4, 9] (30)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 32
                                                                                                 Start : 30
                                                                                    Whitespace : None
                                                                  IterAfter  : [6, 1] (32)
                                                                  IterBefore : [4, 5] (26)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [6, 1] (32)
                                                IterBefore : [4, 5] (26)
                                                Type       : (Lower Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [6, 1] (32)
                              IterBefore : [4, 5] (26)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [6, 1] (32)
                                                                  IterBefore : [6, 1] (32)
                                                                  Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                               -- empty dict --
                                                                  Whitespace : None
                                                IterAfter  : [6, 1] (32)
                                                IterBefore : [6, 1] (32)
                                                Type       : (Lower Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [6, 1] (32)
                              IterBefore : [6, 1] (32)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         6)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 5] (36)
                                                                                    IterBefore : [6, 1] (32)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(32, 36), match='FIVE'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [7, 1] (37)
                                                                                    IterBefore : [6, 5] (36)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 37
                                                                                                 Start : 36
                                                                                    Whitespace : None
                                                                  IterAfter  : [7, 1] (37)
                                                                  IterBefore : [6, 1] (32)
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [7, 1] (37)
                                                IterBefore : [6, 1] (32)
                                                Type       : (Upper Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [7, 1] (37)
                              IterBefore : [6, 1] (32)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [7, 1] (37)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NoMatch(self, parse_mock):
        parse_mock.OnIndentAsync = CoroutineMock(
            return_value=DynamicPhrasesInfo(
                (),
                (),
                (self._lower_phrase, self._dedent_phrase),
                (),
                False,
            ),
        )

        with pytest.raises(SyntaxInvalidError) as ex:
            result = await ParseAsync(
                self._phrases,
                CreateIterator(
                    textwrap.dedent(
                        """\
                        ONE
                            two
                            three
                            four

                        five
                        """,
                    ),
                ),
                parse_mock,
            )

            assert result is None, result

        ex = ex.value

        assert str(ex) == "The syntax is not recognized"
        assert ex.Line == 6
        assert ex.Column == 1

        assert ex.ToDebugString() == textwrap.dedent(
            """\
            The syntax is not recognized [6, 1]

            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [1, 4] (3)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='ONE'>
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
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [2, 1] (4)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Upper Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 1] (4)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [2, 5] (8)
                                                                  IterBefore : [2, 1] (4)
                                                                  Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                               End   : 8
                                                                               Start : 4
                                                                               Value : 4
                                                                  Whitespace : None
                                                IterAfter  : [2, 5] (8)
                                                IterBefore : [2, 1] (4)
                                                Type       : (Upper Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [2, 5] (8)
                              IterBefore : [2, 1] (4)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [2, 8] (11)
                                                                                    IterBefore : [2, 5] (8)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(8, 11), match='two'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 1] (12)
                                                                                    IterBefore : [2, 8] (11)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 12
                                                                                                 Start : 11
                                                                                    Whitespace : None
                                                                  IterAfter  : [3, 1] (12)
                                                                  IterBefore : [2, 5] (8)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [3, 1] (12)
                                                IterBefore : [2, 5] (8)
                                                Type       : (Lower Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [3, 1] (12)
                              IterBefore : [2, 5] (8)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [3, 10] (21)
                                                                                    IterBefore : [3, 5] (16)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(16, 21), match='three'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 1] (22)
                                                                                    IterBefore : [3, 10] (21)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 22
                                                                                                 Start : 21
                                                                                    Whitespace : None
                                                                  IterAfter  : [4, 1] (22)
                                                                  IterBefore : [3, 5] (16)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (22)
                                                IterBefore : [3, 5] (16)
                                                Type       : (Lower Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (22)
                              IterBefore : [3, 5] (16)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         4)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [4, 9] (30)
                                                                                    IterBefore : [4, 5] (26)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(26, 30), match='four'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 1] (32)
                                                                                    IterBefore : [4, 9] (30)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 32
                                                                                                 Start : 30
                                                                                    Whitespace : None
                                                                  IterAfter  : [6, 1] (32)
                                                                  IterBefore : [4, 5] (26)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [6, 1] (32)
                                                IterBefore : [4, 5] (26)
                                                Type       : (Lower Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [6, 1] (32)
                              IterBefore : [4, 5] (26)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         5)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                  IsIgnored  : False
                                                                  IterAfter  : [6, 1] (32)
                                                                  IterBefore : [6, 1] (32)
                                                                  Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                               -- empty dict --
                                                                  Whitespace : None
                                                IterAfter  : [6, 1] (32)
                                                IterBefore : [6, 1] (32)
                                                Type       : (Lower Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [6, 1] (32)
                              IterBefore : [6, 1] (32)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         6)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : -- empty list --
                                                                                    IterAfter  : None
                                                                                    IterBefore : None
                                                                                    Type       : Upper <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Upper Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                             1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : -- empty list --
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Indent Phrase <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                             2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : -- empty list --
                                                                  IterAfter  : None
                                                                  IterBefore : None
                                                                  Type       : Dedent Phrase <class 'TheLanguage.Parser.Phrases.TokenPhrase.TokenPhrase'>
                                                IterAfter  : None
                                                IterBefore : None
                                                Type       : (Upper Phrase, Indent Phrase, Dedent Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
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
async def test_InvalidDynamicTraversalError(parse_mock):
    parse_mock.OnPhraseCompleteAsync = CoroutineMock(
        return_value=DynamicPhrasesInfo(
            (),
            (),
            (CreatePhrase(name="Newline", item=NewlineToken()),),
            (),
            False,
        ),
    )

    with pytest.raises(InvalidDynamicTraversalError) as ex:
        result = await ParseAsync(
            DynamicPhrasesInfo(
                (),
                (),
                (CreatePhrase(name="Newline", item=NewlineToken()),),
                (),
            ),
            CreateIterator(
                textwrap.dedent(
                    """\



                    """,
                ),
            ),
            parse_mock,
        )

        assert result is None, result

    ex = ex.value

    assert str(ex) == "Dynamic phrases that prohibit parent traversal should never be applied over other dynamic phrases within the same lexical scope; consider making these dyanmic phrases the first ones applied in this lexical scope."
    assert ex.Line == 4
    assert ex.Column == 1

# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_DynamicExpressions(parse_mock):
    result = await ParseAsync(
        DynamicPhrasesInfo(
            (
                CreatePhrase(
                    name="Expression",
                    item=_number_token,
                ),
            ),
            (),
            (
                CreatePhrase(
                    name="Statement",
                    item=[
                        _upper_token,
                        DynamicPhrasesType.Expressions,
                        _lower_token,
                        NewlineToken(),
                    ],
                ),
            ),
            (),
        ),
        CreateIterator("WORD 1234 lower"),
        parse_mock,
    )

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
                                                                                Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(0, 4), match='WORD'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                    IsIgnored  : False
                                                                                                                    IterAfter  : [1, 10] (9)
                                                                                                                    IterBefore : [1, 6] (5)
                                                                                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                 Match : <_sre.SRE_Match object; span=(5, 9), match='1234'>
                                                                                                                    Whitespace : 0)   4
                                                                                                                                 1)   5
                                                                                                  IterAfter  : [1, 10] (9)
                                                                                                  IterBefore : [1, 6] (5)
                                                                                                  Type       : (Expression) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 10] (9)
                                                                                IterBefore : [1, 6] (5)
                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 16] (15)
                                                                                IterBefore : [1, 11] (10)
                                                                                Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(10, 15), match='lower'>
                                                                                Whitespace : 0)   9
                                                                                             1)   10
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (16)
                                                                                IterBefore : [1, 16] (15)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 16
                                                                                             Start : 15
                                                                                Whitespace : None
                                                              IterAfter  : [2, 1] (16)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (16)
                                            IterBefore : [1, 1] (0)
                                            Type       : (Statement) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (16)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [2, 1] (16)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
class TestCatastrophicInclude(object):
    _include_phrase                         = CreatePhrase(
        name="Include Phrase",
        item=[
            RegexToken("include", re.compile(r"include")),
            _upper_token,
            NewlineToken(),
        ],
    )

    # Both of these phrases start with an include, but the
    # dynamic phrases allowed will be based on the included
    # value.
    _lower_include_phrase                   = CreatePhrase(
        name="Lower Include Phrase",
        item=[
            _include_phrase,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
        ],
    )

    _number_include_phrase                  = CreatePhrase(
        name="Number Include Phrase",
        item=[
            _include_phrase,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
            DynamicPhrasesType.Statements,
        ],
    )

    _lower_phrase                           = CreatePhrase(
        name="Lower Phrase",
        item=[
            _lower_token,
            NewlineToken(),
        ],
    )

    _number_phrase                          = CreatePhrase(
        name="Number Phrase",
        item=[
            _number_token,
            NewlineToken(),
        ],
    )

    _phrases                                = DynamicPhrasesInfo(
        (),
        (),
        (_lower_include_phrase, _number_include_phrase),
        (),
    )

    _lower_dynamic_phrases                  = DynamicPhrasesInfo(
        (),
        (),
        (_lower_phrase,),
        (),
        True,
        # "Lower Dynamic Phrases",
    )

    _number_dynamic_phrases                 = DynamicPhrasesInfo(
        (),
        (),
        (_number_phrase,),
        (),
        True,
        # "Number Dynamic Phrases",
    )

    # ----------------------------------------------------------------------
    @classmethod
    @pytest.fixture
    def this_parse_mock(cls, parse_mock):
        # ----------------------------------------------------------------------
        async def OnPhraseCompleteAsync(
            phrase: Phrase,
            node: Node,
            iter_before: Phrase.NormalizedIterator,
            iter_after: Phrase.NormalizedIterator,
        ):
            if phrase == cls._include_phrase:
                value = node.Children[1].Value.Match.group("value")

                if value == "LOWER":
                    return cls._lower_dynamic_phrases
                elif value == "NUMBER":
                    return cls._number_dynamic_phrases
                else:
                    assert False, value

            return True

        # ----------------------------------------------------------------------

        parse_mock.OnPhraseCompleteAsync = OnPhraseCompleteAsync

        return parse_mock

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Lower(self, this_parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include LOWER
                    one
                    two
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 8] (7)
                                                                                                      IterBefore : [1, 1] (0)
                                                                                                      Type       : include <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 7), match='include'>
                                                                                                      Whitespace : None
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 14] (13)
                                                                                                      IterBefore : [1, 9] (8)
                                                                                                      Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(8, 13), match='LOWER'>
                                                                                                      Whitespace : 0)   7
                                                                                                                   1)   8
                                                                                                 2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [2, 1] (14)
                                                                                                      IterBefore : [1, 14] (13)
                                                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                   End   : 14
                                                                                                                   Start : 13
                                                                                                      Whitespace : None
                                                                                    IterAfter  : [2, 1] (14)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Include Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [2, 4] (17)
                                                                                                                                          IterBefore : [2, 1] (14)
                                                                                                                                          Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(14, 17), match='one'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 1] (18)
                                                                                                                                          IterBefore : [2, 4] (17)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 18
                                                                                                                                                       Start : 17
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [3, 1] (18)
                                                                                                                        IterBefore : [2, 1] (14)
                                                                                                                        Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [3, 1] (18)
                                                                                                      IterBefore : [2, 1] (14)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [3, 1] (18)
                                                                                    IterBefore : [2, 1] (14)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 4] (21)
                                                                                                                                          IterBefore : [3, 1] (18)
                                                                                                                                          Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(18, 21), match='two'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [4, 1] (22)
                                                                                                                                          IterBefore : [3, 4] (21)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 22
                                                                                                                                                       Start : 21
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [4, 1] (22)
                                                                                                                        IterBefore : [3, 1] (18)
                                                                                                                        Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [4, 1] (22)
                                                                                                      IterBefore : [3, 1] (18)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [4, 1] (22)
                                                                                    IterBefore : [3, 1] (18)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                  IterAfter  : [4, 1] (22)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Lower Include Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [4, 1] (22)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Lower Include Phrase, Number Include Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [4, 1] (22)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [4, 1] (22)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_LowerAdditionalItem(self, this_parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include LOWER
                    one
                    two

                    three
                    four
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 8] (7)
                                                                                                      IterBefore : [1, 1] (0)
                                                                                                      Type       : include <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 7), match='include'>
                                                                                                      Whitespace : None
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 14] (13)
                                                                                                      IterBefore : [1, 9] (8)
                                                                                                      Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(8, 13), match='LOWER'>
                                                                                                      Whitespace : 0)   7
                                                                                                                   1)   8
                                                                                                 2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [2, 1] (14)
                                                                                                      IterBefore : [1, 14] (13)
                                                                                                      Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                   End   : 14
                                                                                                                   Start : 13
                                                                                                      Whitespace : None
                                                                                    IterAfter  : [2, 1] (14)
                                                                                    IterBefore : [1, 1] (0)
                                                                                    Type       : Include Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [2, 4] (17)
                                                                                                                                          IterBefore : [2, 1] (14)
                                                                                                                                          Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(14, 17), match='one'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 1] (18)
                                                                                                                                          IterBefore : [2, 4] (17)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 18
                                                                                                                                                       Start : 17
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [3, 1] (18)
                                                                                                                        IterBefore : [2, 1] (14)
                                                                                                                        Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [3, 1] (18)
                                                                                                      IterBefore : [2, 1] (14)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [3, 1] (18)
                                                                                    IterBefore : [2, 1] (14)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 4] (21)
                                                                                                                                          IterBefore : [3, 1] (18)
                                                                                                                                          Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(18, 21), match='two'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [5, 1] (23)
                                                                                                                                          IterBefore : [3, 4] (21)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 23
                                                                                                                                                       Start : 21
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [5, 1] (23)
                                                                                                                        IterBefore : [3, 1] (18)
                                                                                                                        Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [5, 1] (23)
                                                                                                      IterBefore : [3, 1] (18)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [5, 1] (23)
                                                                                    IterBefore : [3, 1] (18)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [5, 6] (28)
                                                                                                                                          IterBefore : [5, 1] (23)
                                                                                                                                          Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(23, 28), match='three'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [6, 1] (29)
                                                                                                                                          IterBefore : [5, 6] (28)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 29
                                                                                                                                                       Start : 28
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [6, 1] (29)
                                                                                                                        IterBefore : [5, 1] (23)
                                                                                                                        Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [6, 1] (29)
                                                                                                      IterBefore : [5, 1] (23)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [6, 1] (29)
                                                                                    IterBefore : [5, 1] (23)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                  IterAfter  : [6, 1] (29)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Number Include Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [6, 1] (29)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Lower Include Phrase, Number Include Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [6, 1] (29)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 5] (33)
                                                                                    IterBefore : [6, 1] (29)
                                                                                    Type       : Lower <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(29, 33), match='four'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [7, 1] (34)
                                                                                    IterBefore : [6, 5] (33)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 34
                                                                                                 Start : 33
                                                                                    Whitespace : None
                                                                  IterAfter  : [7, 1] (34)
                                                                  IterBefore : [6, 1] (29)
                                                                  Type       : Lower Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [7, 1] (34)
                                                IterBefore : [6, 1] (29)
                                                Type       : (Lower Include Phrase, Number Include Phrase) / (Lower Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [7, 1] (34)
                              IterBefore : [6, 1] (29)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [7, 1] (34)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_Number(self, this_parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include NUMBER
                    1
                    2
                    3
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 8] (7)
                                                                                                      IterBefore : [1, 1] (0)
                                                                                                      Type       : include <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 7), match='include'>
                                                                                                      Whitespace : None
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 15] (14)
                                                                                                      IterBefore : [1, 9] (8)
                                                                                                      Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(8, 14), match='NUMBER'>
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
                                                                                    Type       : Include Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [2, 2] (16)
                                                                                                                                          IterBefore : [2, 1] (15)
                                                                                                                                          Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(15, 16), match='1'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 1] (17)
                                                                                                                                          IterBefore : [2, 2] (16)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 17
                                                                                                                                                       Start : 16
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [3, 1] (17)
                                                                                                                        IterBefore : [2, 1] (15)
                                                                                                                        Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [3, 1] (17)
                                                                                                      IterBefore : [2, 1] (15)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [3, 1] (17)
                                                                                    IterBefore : [2, 1] (15)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 2] (18)
                                                                                                                                          IterBefore : [3, 1] (17)
                                                                                                                                          Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(17, 18), match='2'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [4, 1] (19)
                                                                                                                                          IterBefore : [3, 2] (18)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 19
                                                                                                                                                       Start : 18
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [4, 1] (19)
                                                                                                                        IterBefore : [3, 1] (17)
                                                                                                                        Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [4, 1] (19)
                                                                                                      IterBefore : [3, 1] (17)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [4, 1] (19)
                                                                                    IterBefore : [3, 1] (17)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [4, 2] (20)
                                                                                                                                          IterBefore : [4, 1] (19)
                                                                                                                                          Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(19, 20), match='3'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [5, 1] (21)
                                                                                                                                          IterBefore : [4, 2] (20)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 21
                                                                                                                                                       Start : 20
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [5, 1] (21)
                                                                                                                        IterBefore : [4, 1] (19)
                                                                                                                        Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [5, 1] (21)
                                                                                                      IterBefore : [4, 1] (19)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [5, 1] (21)
                                                                                    IterBefore : [4, 1] (19)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                  IterAfter  : [5, 1] (21)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Number Include Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [5, 1] (21)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Lower Include Phrase, Number Include Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [5, 1] (21)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [5, 1] (21)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert this_parse_mock.method_calls == []

    # ----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_NumberAdditionalItems(self, this_parse_mock):
        result = await ParseAsync(
            self._phrases,
            CreateIterator(
                textwrap.dedent(
                    """\
                    include NUMBER
                    1
                    2
                    3

                    4
                    5
                    """,
                ),
            ),
            this_parse_mock,
        )

        assert str(result) == textwrap.dedent(
            """\
            <class 'TheLanguage.Parser.Components.AST.RootNode'>
            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 8] (7)
                                                                                                      IterBefore : [1, 1] (0)
                                                                                                      Type       : include <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 7), match='include'>
                                                                                                      Whitespace : None
                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                      IsIgnored  : False
                                                                                                      IterAfter  : [1, 15] (14)
                                                                                                      IterBefore : [1, 9] (8)
                                                                                                      Type       : Upper <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                   Match : <_sre.SRE_Match object; span=(8, 14), match='NUMBER'>
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
                                                                                    Type       : Include Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [2, 2] (16)
                                                                                                                                          IterBefore : [2, 1] (15)
                                                                                                                                          Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(15, 16), match='1'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 1] (17)
                                                                                                                                          IterBefore : [2, 2] (16)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 17
                                                                                                                                                       Start : 16
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [3, 1] (17)
                                                                                                                        IterBefore : [2, 1] (15)
                                                                                                                        Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [3, 1] (17)
                                                                                                      IterBefore : [2, 1] (15)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [3, 1] (17)
                                                                                    IterBefore : [2, 1] (15)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [3, 2] (18)
                                                                                                                                          IterBefore : [3, 1] (17)
                                                                                                                                          Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(17, 18), match='2'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [4, 1] (19)
                                                                                                                                          IterBefore : [3, 2] (18)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 19
                                                                                                                                                       Start : 18
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [4, 1] (19)
                                                                                                                        IterBefore : [3, 1] (17)
                                                                                                                        Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [4, 1] (19)
                                                                                                      IterBefore : [3, 1] (17)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [4, 1] (19)
                                                                                    IterBefore : [3, 1] (17)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [4, 2] (20)
                                                                                                                                          IterBefore : [4, 1] (19)
                                                                                                                                          Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                       Match : <_sre.SRE_Match object; span=(19, 20), match='3'>
                                                                                                                                          Whitespace : None
                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                          IsIgnored  : False
                                                                                                                                          IterAfter  : [6, 1] (22)
                                                                                                                                          IterBefore : [4, 2] (20)
                                                                                                                                          Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                       End   : 22
                                                                                                                                                       Start : 20
                                                                                                                                          Whitespace : None
                                                                                                                        IterAfter  : [6, 1] (22)
                                                                                                                        IterBefore : [4, 1] (19)
                                                                                                                        Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                      IterAfter  : [6, 1] (22)
                                                                                                      IterBefore : [4, 1] (19)
                                                                                                      Type       : (Lower Include Phrase, Number Include Phrase) / (Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                    IterAfter  : [6, 1] (22)
                                                                                    IterBefore : [4, 1] (19)
                                                                                    Type       : DynamicPhrasesType.Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                  IterAfter  : [6, 1] (22)
                                                                  IterBefore : [1, 1] (0)
                                                                  Type       : Number Include Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [6, 1] (22)
                                                IterBefore : [1, 1] (0)
                                                Type       : (Lower Include Phrase, Number Include Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [6, 1] (22)
                              IterBefore : [1, 1] (0)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [6, 2] (23)
                                                                                    IterBefore : [6, 1] (22)
                                                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(22, 23), match='4'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [7, 1] (24)
                                                                                    IterBefore : [6, 2] (23)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 24
                                                                                                 Start : 23
                                                                                    Whitespace : None
                                                                  IterAfter  : [7, 1] (24)
                                                                  IterBefore : [6, 1] (22)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [7, 1] (24)
                                                IterBefore : [6, 1] (22)
                                                Type       : (Lower Include Phrase, Number Include Phrase) / (Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [7, 1] (24)
                              IterBefore : [6, 1] (22)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                         2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [7, 2] (25)
                                                                                    IterBefore : [7, 1] (24)
                                                                                    Type       : Number <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                 Match : <_sre.SRE_Match object; span=(24, 25), match='5'>
                                                                                    Whitespace : None
                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                    IsIgnored  : False
                                                                                    IterAfter  : [8, 1] (26)
                                                                                    IterBefore : [7, 2] (25)
                                                                                    Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                 End   : 26
                                                                                                 Start : 25
                                                                                    Whitespace : None
                                                                  IterAfter  : [8, 1] (26)
                                                                  IterBefore : [7, 1] (24)
                                                                  Type       : Number Phrase <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                IterAfter  : [8, 1] (26)
                                                IterBefore : [7, 1] (24)
                                                Type       : (Lower Include Phrase, Number Include Phrase) / (Number Phrase) <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                              IterAfter  : [8, 1] (26)
                              IterBefore : [7, 1] (24)
                              Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
            IterAfter  : [8, 1] (26)
            IterBefore : [1, 1] (0)
            Type       : <None>
            """,
        )

        assert this_parse_mock.method_calls == []
