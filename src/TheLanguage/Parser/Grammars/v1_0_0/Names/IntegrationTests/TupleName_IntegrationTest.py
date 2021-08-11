# ----------------------------------------------------------------------
# |
# |  TupleName_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 22:12:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TupleName"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleName import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Single():
    assert Execute(
        textwrap.dedent(
            """\
            (a,) = value1
            (b,) = value2

            ( # Comment 1
              b # Comment 2
            ,) = value3
            """,
        ),
    ) == textwrap.dedent(
        """\
        <class 'TheLanguage.Parser.Components.AST.RootNode'>
        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [1, 2] (1)
                                                                                                                                                        IterBefore : [1, 1] (0)
                                                                                                                                                        Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(0, 1), match='('>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                                                              IterAfter  : [1, 3] (2)
                                                                                                                                                                                                              IterBefore : [1, 2] (1)
                                                                                                                                                                                                              Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(1, 2), match='a'>
                                                                                                                                                                                                              Whitespace : None
                                                                                                                                                                                            IterAfter  : [1, 3] (2)
                                                                                                                                                                                            IterBefore : [1, 2] (1)
                                                                                                                                                                                            Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                          IterAfter  : [1, 3] (2)
                                                                                                                                                                          IterBefore : [1, 2] (1)
                                                                                                                                                                          Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                        IterAfter  : [1, 3] (2)
                                                                                                                                                        IterBefore : [1, 2] (1)
                                                                                                                                                        Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [1, 4] (3)
                                                                                                                                                        IterBefore : [1, 3] (2)
                                                                                                                                                        Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(2, 3), match=','>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [1, 5] (4)
                                                                                                                                                        IterBefore : [1, 4] (3)
                                                                                                                                                        Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(3, 4), match=')'>
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [1, 5] (4)
                                                                                                                                      IterBefore : [1, 1] (0)
                                                                                                                                      Type       : Single <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [1, 5] (4)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : Tuple Name <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [1, 5] (4)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 5] (4)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 7] (6)
                                                                                IterBefore : [1, 6] (5)
                                                                                Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(5, 6), match='='>
                                                                                Whitespace : 0)   4
                                                                                             1)   5
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [1, 14] (13)
                                                                                                                                                                          IterBefore : [1, 8] (7)
                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(7, 13), match='value1'>
                                                                                                                                                                          Whitespace : 0)   6
                                                                                                                                                                                       1)   7
                                                                                                                                                        IterAfter  : [1, 14] (13)
                                                                                                                                                        IterBefore : [1, 8] (7)
                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [1, 14] (13)
                                                                                                                                      IterBefore : [1, 8] (7)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [1, 14] (13)
                                                                                                                    IterBefore : [1, 8] (7)
                                                                                                                    Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [1, 14] (13)
                                                                                                  IterBefore : [1, 8] (7)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 14] (13)
                                                                                IterBefore : [1, 8] (7)
                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
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
                                                              Type       : Variable Declaration Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (14)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (14)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [2, 2] (15)
                                                                                                                                                        IterBefore : [2, 1] (14)
                                                                                                                                                        Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(14, 15), match='('>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                                                              IterAfter  : [2, 3] (16)
                                                                                                                                                                                                              IterBefore : [2, 2] (15)
                                                                                                                                                                                                              Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(15, 16), match='b'>
                                                                                                                                                                                                              Whitespace : None
                                                                                                                                                                                            IterAfter  : [2, 3] (16)
                                                                                                                                                                                            IterBefore : [2, 2] (15)
                                                                                                                                                                                            Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                          IterAfter  : [2, 3] (16)
                                                                                                                                                                          IterBefore : [2, 2] (15)
                                                                                                                                                                          Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                        IterAfter  : [2, 3] (16)
                                                                                                                                                        IterBefore : [2, 2] (15)
                                                                                                                                                        Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [2, 4] (17)
                                                                                                                                                        IterBefore : [2, 3] (16)
                                                                                                                                                        Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(16, 17), match=','>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [2, 5] (18)
                                                                                                                                                        IterBefore : [2, 4] (17)
                                                                                                                                                        Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(17, 18), match=')'>
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [2, 5] (18)
                                                                                                                                      IterBefore : [2, 1] (14)
                                                                                                                                      Type       : Single <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [2, 5] (18)
                                                                                                                    IterBefore : [2, 1] (14)
                                                                                                                    Type       : Tuple Name <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [2, 5] (18)
                                                                                                  IterBefore : [2, 1] (14)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [2, 5] (18)
                                                                                IterBefore : [2, 1] (14)
                                                                                Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 7] (20)
                                                                                IterBefore : [2, 6] (19)
                                                                                Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(19, 20), match='='>
                                                                                Whitespace : 0)   18
                                                                                             1)   19
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [2, 14] (27)
                                                                                                                                                                          IterBefore : [2, 8] (21)
                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(21, 27), match='value2'>
                                                                                                                                                                          Whitespace : 0)   20
                                                                                                                                                                                       1)   21
                                                                                                                                                        IterAfter  : [2, 14] (27)
                                                                                                                                                        IterBefore : [2, 8] (21)
                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [2, 14] (27)
                                                                                                                                      IterBefore : [2, 8] (21)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [2, 14] (27)
                                                                                                                    IterBefore : [2, 8] (21)
                                                                                                                    Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [2, 14] (27)
                                                                                                  IterBefore : [2, 8] (21)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [2, 14] (27)
                                                                                IterBefore : [2, 8] (21)
                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 1] (29)
                                                                                IterBefore : [2, 14] (27)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 29
                                                                                             Start : 27
                                                                                Whitespace : None
                                                              IterAfter  : [4, 1] (29)
                                                              IterBefore : [2, 1] (14)
                                                              Type       : Variable Declaration Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [4, 1] (29)
                                            IterBefore : [2, 1] (14)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [4, 1] (29)
                          IterBefore : [2, 1] (14)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [4, 2] (30)
                                                                                                                                                        IterBefore : [4, 1] (29)
                                                                                                                                                        Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(29, 30), match='('>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                                                              IterAfter  : [5, 4] (46)
                                                                                                                                                                                                              IterBefore : [5, 3] (45)
                                                                                                                                                                                                              Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(45, 46), match='b'>
                                                                                                                                                                                                              Whitespace : None
                                                                                                                                                                                            IterAfter  : [5, 4] (46)
                                                                                                                                                                                            IterBefore : [5, 3] (45)
                                                                                                                                                                                            Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                          IterAfter  : [5, 4] (46)
                                                                                                                                                                          IterBefore : [5, 3] (45)
                                                                                                                                                                          Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                        IterAfter  : [5, 4] (46)
                                                                                                                                                        IterBefore : [5, 3] (45)
                                                                                                                                                        Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [6, 2] (60)
                                                                                                                                                        IterBefore : [6, 1] (59)
                                                                                                                                                        Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(59, 60), match=','>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [6, 3] (61)
                                                                                                                                                        IterBefore : [6, 2] (60)
                                                                                                                                                        Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(60, 61), match=')'>
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [6, 3] (61)
                                                                                                                                      IterBefore : [4, 1] (29)
                                                                                                                                      Type       : Single <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [6, 3] (61)
                                                                                                                    IterBefore : [4, 1] (29)
                                                                                                                    Type       : Tuple Name <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [6, 3] (61)
                                                                                                  IterBefore : [4, 1] (29)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [6, 3] (61)
                                                                                IterBefore : [4, 1] (29)
                                                                                Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [6, 5] (63)
                                                                                IterBefore : [6, 4] (62)
                                                                                Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(62, 63), match='='>
                                                                                Whitespace : 0)   61
                                                                                             1)   62
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [6, 12] (70)
                                                                                                                                                                          IterBefore : [6, 6] (64)
                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(64, 70), match='value3'>
                                                                                                                                                                          Whitespace : 0)   63
                                                                                                                                                                                       1)   64
                                                                                                                                                        IterAfter  : [6, 12] (70)
                                                                                                                                                        IterBefore : [6, 6] (64)
                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [6, 12] (70)
                                                                                                                                      IterBefore : [6, 6] (64)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [6, 12] (70)
                                                                                                                    IterBefore : [6, 6] (64)
                                                                                                                    Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [6, 12] (70)
                                                                                                  IterBefore : [6, 6] (64)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [6, 12] (70)
                                                                                IterBefore : [6, 6] (64)
                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [7, 1] (71)
                                                                                IterBefore : [6, 12] (70)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 71
                                                                                             Start : 70
                                                                                Whitespace : None
                                                              IterAfter  : [7, 1] (71)
                                                              IterBefore : [4, 1] (29)
                                                              Type       : Variable Declaration Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [7, 1] (71)
                                            IterBefore : [4, 1] (29)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [7, 1] (71)
                          IterBefore : [4, 1] (29)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [7, 1] (71)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_Multiple():
    assert Execute(
        textwrap.dedent(
            """\
            (a, (b, c), d,) = value
            """,
        ),
    ) == textwrap.dedent(
        """\
        <class 'TheLanguage.Parser.Components.AST.RootNode'>
        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [1, 2] (1)
                                                                                                                                                        IterBefore : [1, 1] (0)
                                                                                                                                                        Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(0, 1), match='('>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                                                              IterAfter  : [1, 3] (2)
                                                                                                                                                                                                              IterBefore : [1, 2] (1)
                                                                                                                                                                                                              Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(1, 2), match='a'>
                                                                                                                                                                                                              Whitespace : None
                                                                                                                                                                                            IterAfter  : [1, 3] (2)
                                                                                                                                                                                            IterBefore : [1, 2] (1)
                                                                                                                                                                                            Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                          IterAfter  : [1, 3] (2)
                                                                                                                                                                          IterBefore : [1, 2] (1)
                                                                                                                                                                          Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                        IterAfter  : [1, 3] (2)
                                                                                                                                                        IterBefore : [1, 2] (1)
                                                                                                                                                        Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                   2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [1, 4] (3)
                                                                                                                                                                                            IterBefore : [1, 3] (2)
                                                                                                                                                                                            Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(2, 3), match=','>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                                                    IterAfter  : [1, 6] (5)
                                                                                                                                                                                                                                                                    IterBefore : [1, 5] (4)
                                                                                                                                                                                                                                                                    Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(4, 5), match='('>
                                                                                                                                                                                                                                                                    Whitespace : 0)   3
                                                                                                                                                                                                                                                                                 1)   4
                                                                                                                                                                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                                                                                                                                                                          IterAfter  : [1, 7] (6)
                                                                                                                                                                                                                                                                                                                          IterBefore : [1, 6] (5)
                                                                                                                                                                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(5, 6), match='b'>
                                                                                                                                                                                                                                                                                                                          Whitespace : None
                                                                                                                                                                                                                                                                                                        IterAfter  : [1, 7] (6)
                                                                                                                                                                                                                                                                                                        IterBefore : [1, 6] (5)
                                                                                                                                                                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                                                      IterAfter  : [1, 7] (6)
                                                                                                                                                                                                                                                                                      IterBefore : [1, 6] (5)
                                                                                                                                                                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                                                    IterAfter  : [1, 7] (6)
                                                                                                                                                                                                                                                                    IterBefore : [1, 6] (5)
                                                                                                                                                                                                                                                                    Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                                                                               2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                                        IsIgnored  : False
                                                                                                                                                                                                                                                                                                        IterAfter  : [1, 8] (7)
                                                                                                                                                                                                                                                                                                        IterBefore : [1, 7] (6)
                                                                                                                                                                                                                                                                                                        Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(6, 7), match=','>
                                                                                                                                                                                                                                                                                                        Whitespace : None
                                                                                                                                                                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                                                                                                                                                                                                              IterAfter  : [1, 10] (9)
                                                                                                                                                                                                                                                                                                                                                              IterBefore : [1, 9] (8)
                                                                                                                                                                                                                                                                                                                                                              Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(8, 9), match='c'>
                                                                                                                                                                                                                                                                                                                                                              Whitespace : 0)   7
                                                                                                                                                                                                                                                                                                                                                                           1)   8
                                                                                                                                                                                                                                                                                                                                            IterAfter  : [1, 10] (9)
                                                                                                                                                                                                                                                                                                                                            IterBefore : [1, 9] (8)
                                                                                                                                                                                                                                                                                                                                            Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                                                                                          IterAfter  : [1, 10] (9)
                                                                                                                                                                                                                                                                                                                          IterBefore : [1, 9] (8)
                                                                                                                                                                                                                                                                                                                          Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                                                                                        IterAfter  : [1, 10] (9)
                                                                                                                                                                                                                                                                                                        IterBefore : [1, 9] (8)
                                                                                                                                                                                                                                                                                                        Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                                                                                                      IterAfter  : [1, 10] (9)
                                                                                                                                                                                                                                                                                      IterBefore : [1, 7] (6)
                                                                                                                                                                                                                                                                                      Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                                    IterAfter  : [1, 10] (9)
                                                                                                                                                                                                                                                                    IterBefore : [1, 7] (6)
                                                                                                                                                                                                                                                                    Type       : Repeat: {Comma and Element, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                                                                                                               3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                                                    IterAfter  : [1, 11] (10)
                                                                                                                                                                                                                                                                    IterBefore : [1, 10] (9)
                                                                                                                                                                                                                                                                    Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(9, 10), match=')'>
                                                                                                                                                                                                                                                                    Whitespace : None
                                                                                                                                                                                                                                                  IterAfter  : [1, 11] (10)
                                                                                                                                                                                                                                                  IterBefore : [1, 5] (4)
                                                                                                                                                                                                                                                  Type       : Multiple <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                IterAfter  : [1, 11] (10)
                                                                                                                                                                                                                                IterBefore : [1, 5] (4)
                                                                                                                                                                                                                                Type       : Tuple Name <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                              IterAfter  : [1, 11] (10)
                                                                                                                                                                                                              IterBefore : [1, 5] (4)
                                                                                                                                                                                                              Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                            IterAfter  : [1, 11] (10)
                                                                                                                                                                                            IterBefore : [1, 5] (4)
                                                                                                                                                                                            Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                          IterAfter  : [1, 11] (10)
                                                                                                                                                                          IterBefore : [1, 3] (2)
                                                                                                                                                                          Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [1, 12] (11)
                                                                                                                                                                                            IterBefore : [1, 11] (10)
                                                                                                                                                                                            Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(10, 11), match=','>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                  IsIgnored  : False
                                                                                                                                                                                                                                                  IterAfter  : [1, 14] (13)
                                                                                                                                                                                                                                                  IterBefore : [1, 13] (12)
                                                                                                                                                                                                                                                  Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                  Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                               Match : <_sre.SRE_Match object; span=(12, 13), match='d'>
                                                                                                                                                                                                                                                  Whitespace : 0)   11
                                                                                                                                                                                                                                                               1)   12
                                                                                                                                                                                                                                IterAfter  : [1, 14] (13)
                                                                                                                                                                                                                                IterBefore : [1, 13] (12)
                                                                                                                                                                                                                                Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                              IterAfter  : [1, 14] (13)
                                                                                                                                                                                                              IterBefore : [1, 13] (12)
                                                                                                                                                                                                              Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                            IterAfter  : [1, 14] (13)
                                                                                                                                                                                            IterBefore : [1, 13] (12)
                                                                                                                                                                                            Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                          IterAfter  : [1, 14] (13)
                                                                                                                                                                          IterBefore : [1, 11] (10)
                                                                                                                                                                          Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [1, 14] (13)
                                                                                                                                                        IterBefore : [1, 3] (2)
                                                                                                                                                        Type       : Repeat: {Comma and Element, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                   3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [1, 15] (14)
                                                                                                                                                                          IterBefore : [1, 14] (13)
                                                                                                                                                                          Type       : Trailing Comma <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(13, 14), match=','>
                                                                                                                                                                          Whitespace : None
                                                                                                                                                        IterAfter  : [1, 15] (14)
                                                                                                                                                        IterBefore : [1, 14] (13)
                                                                                                                                                        Type       : Repeat: {Trailing Comma, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                   4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [1, 16] (15)
                                                                                                                                                        IterBefore : [1, 15] (14)
                                                                                                                                                        Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(14, 15), match=')'>
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [1, 16] (15)
                                                                                                                                      IterBefore : [1, 1] (0)
                                                                                                                                      Type       : Multiple <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [1, 16] (15)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : Tuple Name <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [1, 16] (15)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 16] (15)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 18] (17)
                                                                                IterBefore : [1, 17] (16)
                                                                                Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(16, 17), match='='>
                                                                                Whitespace : 0)   15
                                                                                             1)   16
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [1, 24] (23)
                                                                                                                                                                          IterBefore : [1, 19] (18)
                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(18, 23), match='value'>
                                                                                                                                                                          Whitespace : 0)   17
                                                                                                                                                                                       1)   18
                                                                                                                                                        IterAfter  : [1, 24] (23)
                                                                                                                                                        IterBefore : [1, 19] (18)
                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [1, 24] (23)
                                                                                                                                      IterBefore : [1, 19] (18)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [1, 24] (23)
                                                                                                                    IterBefore : [1, 19] (18)
                                                                                                                    Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [1, 24] (23)
                                                                                                  IterBefore : [1, 19] (18)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 24] (23)
                                                                                IterBefore : [1, 19] (18)
                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (24)
                                                                                IterBefore : [1, 24] (23)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 24
                                                                                             Start : 23
                                                                                Whitespace : None
                                                              IterAfter  : [2, 1] (24)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Variable Declaration Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (24)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (24)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [2, 1] (24)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )
