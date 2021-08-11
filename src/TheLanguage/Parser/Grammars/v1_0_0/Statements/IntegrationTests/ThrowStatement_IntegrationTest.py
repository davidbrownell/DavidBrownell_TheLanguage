# ----------------------------------------------------------------------
# |
# |  ThrowStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:39:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for ThrowStatement.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ThrowStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_StandAlone():
    assert Execute(
        textwrap.dedent(
            """\
            throw
            """,
        ),
    ) == textwrap.dedent(
        """\
        <class 'TheLanguage.Parser.Components.AST.RootNode'>
        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 6] (5)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : 'throw' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(0, 5), match='throw'>
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
                                                              Type       : Throw Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (6)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (6)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [2, 1] (6)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )


# ----------------------------------------------------------------------
def test_WithValue():
    assert Execute(
        textwrap.dedent(
            """\
            throw foo
            throw (a, b)
            """,
        ),
    ) == textwrap.dedent(
        """\
        <class 'TheLanguage.Parser.Components.AST.RootNode'>
        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 6] (5)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : 'throw' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(0, 5), match='throw'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [1, 10] (9)
                                                                                                                                                                                            IterBefore : [1, 7] (6)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(6, 9), match='foo'>
                                                                                                                                                                                            Whitespace : 0)   5
                                                                                                                                                                                                         1)   6
                                                                                                                                                                          IterAfter  : [1, 10] (9)
                                                                                                                                                                          IterBefore : [1, 7] (6)
                                                                                                                                                                          Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [1, 10] (9)
                                                                                                                                                        IterBefore : [1, 7] (6)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [1, 10] (9)
                                                                                                                                      IterBefore : [1, 7] (6)
                                                                                                                                      Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                    IterAfter  : [1, 10] (9)
                                                                                                                    IterBefore : [1, 7] (6)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [1, 10] (9)
                                                                                                  IterBefore : [1, 7] (6)
                                                                                                  Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [1, 10] (9)
                                                                                IterBefore : [1, 7] (6)
                                                                                Type       : Repeat: {DynamicPhrasesType.Expressions, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (10)
                                                                                IterBefore : [1, 10] (9)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 10
                                                                                             Start : 9
                                                                                Whitespace : None
                                                              IterAfter  : [2, 1] (10)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Throw Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (10)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (10)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 6] (15)
                                                                                IterBefore : [2, 1] (10)
                                                                                Type       : 'throw' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(10, 15), match='throw'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [2, 8] (17)
                                                                                                                                                                          IterBefore : [2, 7] (16)
                                                                                                                                                                          Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(16, 17), match='('>
                                                                                                                                                                          Whitespace : 0)   15
                                                                                                                                                                                       1)   16
                                                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                                                    IterAfter  : [2, 9] (18)
                                                                                                                                                                                                                                                                    IterBefore : [2, 8] (17)
                                                                                                                                                                                                                                                                    Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(17, 18), match='a'>
                                                                                                                                                                                                                                                                    Whitespace : None
                                                                                                                                                                                                                                                  IterAfter  : [2, 9] (18)
                                                                                                                                                                                                                                                  IterBefore : [2, 8] (17)
                                                                                                                                                                                                                                                  Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                IterAfter  : [2, 9] (18)
                                                                                                                                                                                                                                IterBefore : [2, 8] (17)
                                                                                                                                                                                                                                Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                              IterAfter  : [2, 9] (18)
                                                                                                                                                                                                              IterBefore : [2, 8] (17)
                                                                                                                                                                                                              Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                            IterAfter  : [2, 9] (18)
                                                                                                                                                                                            IterBefore : [2, 8] (17)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [2, 9] (18)
                                                                                                                                                                          IterBefore : [2, 8] (17)
                                                                                                                                                                          Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                     2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                                                              IterAfter  : [2, 10] (19)
                                                                                                                                                                                                              IterBefore : [2, 9] (18)
                                                                                                                                                                                                              Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(18, 19), match=','>
                                                                                                                                                                                                              Whitespace : None
                                                                                                                                                                                                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                                        IsIgnored  : False
                                                                                                                                                                                                                                                                                                        IterAfter  : [2, 12] (21)
                                                                                                                                                                                                                                                                                                        IterBefore : [2, 11] (20)
                                                                                                                                                                                                                                                                                                        Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(20, 21), match='b'>
                                                                                                                                                                                                                                                                                                        Whitespace : 0)   19
                                                                                                                                                                                                                                                                                                                     1)   20
                                                                                                                                                                                                                                                                                      IterAfter  : [2, 12] (21)
                                                                                                                                                                                                                                                                                      IterBefore : [2, 11] (20)
                                                                                                                                                                                                                                                                                      Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                                    IterAfter  : [2, 12] (21)
                                                                                                                                                                                                                                                                    IterBefore : [2, 11] (20)
                                                                                                                                                                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                                  IterAfter  : [2, 12] (21)
                                                                                                                                                                                                                                                  IterBefore : [2, 11] (20)
                                                                                                                                                                                                                                                  Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                                                IterAfter  : [2, 12] (21)
                                                                                                                                                                                                                                IterBefore : [2, 11] (20)
                                                                                                                                                                                                                                Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                              IterAfter  : [2, 12] (21)
                                                                                                                                                                                                              IterBefore : [2, 11] (20)
                                                                                                                                                                                                              Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                            IterAfter  : [2, 12] (21)
                                                                                                                                                                                            IterBefore : [2, 9] (18)
                                                                                                                                                                                            Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                          IterAfter  : [2, 12] (21)
                                                                                                                                                                          IterBefore : [2, 9] (18)
                                                                                                                                                                          Type       : Repeat: {Comma and Element, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                     3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [2, 13] (22)
                                                                                                                                                                          IterBefore : [2, 12] (21)
                                                                                                                                                                          Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(21, 22), match=')'>
                                                                                                                                                                          Whitespace : None
                                                                                                                                                        IterAfter  : [2, 13] (22)
                                                                                                                                                        IterBefore : [2, 7] (16)
                                                                                                                                                        Type       : Multiple <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [2, 13] (22)
                                                                                                                                      IterBefore : [2, 7] (16)
                                                                                                                                      Type       : Tuple Expression <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [2, 13] (22)
                                                                                                                    IterBefore : [2, 7] (16)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [2, 13] (22)
                                                                                                  IterBefore : [2, 7] (16)
                                                                                                  Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [2, 13] (22)
                                                                                IterBefore : [2, 7] (16)
                                                                                Type       : Repeat: {DynamicPhrasesType.Expressions, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [3, 1] (23)
                                                                                IterBefore : [2, 13] (22)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 23
                                                                                             Start : 22
                                                                                Whitespace : None
                                                              IterAfter  : [3, 1] (23)
                                                              IterBefore : [2, 1] (10)
                                                              Type       : Throw Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [3, 1] (23)
                                            IterBefore : [2, 1] (10)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [3, 1] (23)
                          IterBefore : [2, 1] (10)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [3, 1] (23)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )