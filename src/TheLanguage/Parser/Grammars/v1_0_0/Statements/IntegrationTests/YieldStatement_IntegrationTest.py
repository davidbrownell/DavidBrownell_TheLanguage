# ----------------------------------------------------------------------
# |
# |  YieldStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:15:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for YieldStatement.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..YieldStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_StandAlone():
    assert Execute(
        textwrap.dedent(
            """\
            yield
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
                                                                                Type       : 'yield' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(0, 5), match='yield'>
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
                                                              Type       : Yield Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
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
            yield foo
            yield (value,)
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
                                                                                Type       : 'yield' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(0, 5), match='yield'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
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
                                                                                                  Type       : Suffix <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                IterAfter  : [1, 10] (9)
                                                                                IterBefore : [1, 7] (6)
                                                                                Type       : Repeat: {Suffix, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
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
                                                              Type       : Yield Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
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
                                                                                Type       : 'yield' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(10, 15), match='yield'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
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
                                                                                                                                                                                                                                                                                      IterAfter  : [2, 13] (22)
                                                                                                                                                                                                                                                                                      IterBefore : [2, 8] (17)
                                                                                                                                                                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                   Match : <_sre.SRE_Match object; span=(17, 22), match='value'>
                                                                                                                                                                                                                                                                                      Whitespace : None
                                                                                                                                                                                                                                                                    IterAfter  : [2, 13] (22)
                                                                                                                                                                                                                                                                    IterBefore : [2, 8] (17)
                                                                                                                                                                                                                                                                    Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                  IterAfter  : [2, 13] (22)
                                                                                                                                                                                                                                                  IterBefore : [2, 8] (17)
                                                                                                                                                                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                IterAfter  : [2, 13] (22)
                                                                                                                                                                                                                                IterBefore : [2, 8] (17)
                                                                                                                                                                                                                                Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                              IterAfter  : [2, 13] (22)
                                                                                                                                                                                                              IterBefore : [2, 8] (17)
                                                                                                                                                                                                              Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                            IterAfter  : [2, 13] (22)
                                                                                                                                                                                            IterBefore : [2, 8] (17)
                                                                                                                                                                                            Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                       2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [2, 14] (23)
                                                                                                                                                                                            IterBefore : [2, 13] (22)
                                                                                                                                                                                            Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(22, 23), match=','>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                                       3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [2, 15] (24)
                                                                                                                                                                                            IterBefore : [2, 14] (23)
                                                                                                                                                                                            Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(23, 24), match=')'>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                          IterAfter  : [2, 15] (24)
                                                                                                                                                                          IterBefore : [2, 7] (16)
                                                                                                                                                                          Type       : Single <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [2, 15] (24)
                                                                                                                                                        IterBefore : [2, 7] (16)
                                                                                                                                                        Type       : Tuple Expression <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [2, 15] (24)
                                                                                                                                      IterBefore : [2, 7] (16)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [2, 15] (24)
                                                                                                                    IterBefore : [2, 7] (16)
                                                                                                                    Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [2, 15] (24)
                                                                                                  IterBefore : [2, 7] (16)
                                                                                                  Type       : Suffix <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                IterAfter  : [2, 15] (24)
                                                                                IterBefore : [2, 7] (16)
                                                                                Type       : Repeat: {Suffix, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [3, 1] (25)
                                                                                IterBefore : [2, 15] (24)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 25
                                                                                             Start : 24
                                                                                Whitespace : None
                                                              IterAfter  : [3, 1] (25)
                                                              IterBefore : [2, 1] (10)
                                                              Type       : Yield Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [3, 1] (25)
                                            IterBefore : [2, 1] (10)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [3, 1] (25)
                          IterBefore : [2, 1] (10)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [3, 1] (25)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_From():
    assert Execute(
        textwrap.dedent(
            """\
            yield from foo
            yield from (a,b,c)
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
                                                                                Type       : 'yield' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(0, 5), match='yield'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [1, 11] (10)
                                                                                                                                      IterBefore : [1, 7] (6)
                                                                                                                                      Type       : 'from' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(6, 10), match='from'>
                                                                                                                                      Whitespace : 0)   5
                                                                                                                                                   1)   6
                                                                                                                    IterAfter  : [1, 11] (10)
                                                                                                                    IterBefore : [1, 7] (6)
                                                                                                                    Type       : Repeat: {'from', 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                                                              IterAfter  : [1, 15] (14)
                                                                                                                                                                                                              IterBefore : [1, 12] (11)
                                                                                                                                                                                                              Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(11, 14), match='foo'>
                                                                                                                                                                                                              Whitespace : 0)   10
                                                                                                                                                                                                                           1)   11
                                                                                                                                                                                            IterAfter  : [1, 15] (14)
                                                                                                                                                                                            IterBefore : [1, 12] (11)
                                                                                                                                                                                            Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                          IterAfter  : [1, 15] (14)
                                                                                                                                                                          IterBefore : [1, 12] (11)
                                                                                                                                                                          Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                        IterAfter  : [1, 15] (14)
                                                                                                                                                        IterBefore : [1, 12] (11)
                                                                                                                                                        Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                      IterAfter  : [1, 15] (14)
                                                                                                                                      IterBefore : [1, 12] (11)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [1, 15] (14)
                                                                                                                    IterBefore : [1, 12] (11)
                                                                                                                    Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [1, 15] (14)
                                                                                                  IterBefore : [1, 7] (6)
                                                                                                  Type       : Suffix <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                IterAfter  : [1, 15] (14)
                                                                                IterBefore : [1, 7] (6)
                                                                                Type       : Repeat: {Suffix, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
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
                                                              Type       : Yield Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (15)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (15)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 6] (20)
                                                                                IterBefore : [2, 1] (15)
                                                                                Type       : 'yield' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(15, 20), match='yield'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [2, 11] (25)
                                                                                                                                      IterBefore : [2, 7] (21)
                                                                                                                                      Type       : 'from' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(21, 25), match='from'>
                                                                                                                                      Whitespace : 0)   20
                                                                                                                                                   1)   21
                                                                                                                    IterAfter  : [2, 11] (25)
                                                                                                                    IterBefore : [2, 7] (21)
                                                                                                                    Type       : Repeat: {'from', 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [2, 13] (27)
                                                                                                                                                                                            IterBefore : [2, 12] (26)
                                                                                                                                                                                            Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(26, 27), match='('>
                                                                                                                                                                                            Whitespace : 0)   25
                                                                                                                                                                                                         1)   26
                                                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                      IsIgnored  : False
                                                                                                                                                                                                                                                                                      IterAfter  : [2, 14] (28)
                                                                                                                                                                                                                                                                                      IterBefore : [2, 13] (27)
                                                                                                                                                                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                   Match : <_sre.SRE_Match object; span=(27, 28), match='a'>
                                                                                                                                                                                                                                                                                      Whitespace : None
                                                                                                                                                                                                                                                                    IterAfter  : [2, 14] (28)
                                                                                                                                                                                                                                                                    IterBefore : [2, 13] (27)
                                                                                                                                                                                                                                                                    Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                  IterAfter  : [2, 14] (28)
                                                                                                                                                                                                                                                  IterBefore : [2, 13] (27)
                                                                                                                                                                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                IterAfter  : [2, 14] (28)
                                                                                                                                                                                                                                IterBefore : [2, 13] (27)
                                                                                                                                                                                                                                Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                              IterAfter  : [2, 14] (28)
                                                                                                                                                                                                              IterBefore : [2, 13] (27)
                                                                                                                                                                                                              Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                            IterAfter  : [2, 14] (28)
                                                                                                                                                                                            IterBefore : [2, 13] (27)
                                                                                                                                                                                            Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                       2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [2, 15] (29)
                                                                                                                                                                                                                                IterBefore : [2, 14] (28)
                                                                                                                                                                                                                                Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(28, 29), match=','>
                                                                                                                                                                                                                                Whitespace : None
                                                                                                                                                                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                                                                                                                                                                          IterAfter  : [2, 16] (30)
                                                                                                                                                                                                                                                                                                                          IterBefore : [2, 15] (29)
                                                                                                                                                                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(29, 30), match='b'>
                                                                                                                                                                                                                                                                                                                          Whitespace : None
                                                                                                                                                                                                                                                                                                        IterAfter  : [2, 16] (30)
                                                                                                                                                                                                                                                                                                        IterBefore : [2, 15] (29)
                                                                                                                                                                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                                                      IterAfter  : [2, 16] (30)
                                                                                                                                                                                                                                                                                      IterBefore : [2, 15] (29)
                                                                                                                                                                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                                                    IterAfter  : [2, 16] (30)
                                                                                                                                                                                                                                                                    IterBefore : [2, 15] (29)
                                                                                                                                                                                                                                                                    Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                                                                  IterAfter  : [2, 16] (30)
                                                                                                                                                                                                                                                  IterBefore : [2, 15] (29)
                                                                                                                                                                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                IterAfter  : [2, 16] (30)
                                                                                                                                                                                                                                IterBefore : [2, 15] (29)
                                                                                                                                                                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                              IterAfter  : [2, 16] (30)
                                                                                                                                                                                                              IterBefore : [2, 14] (28)
                                                                                                                                                                                                              Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [2, 17] (31)
                                                                                                                                                                                                                                IterBefore : [2, 16] (30)
                                                                                                                                                                                                                                Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(30, 31), match=','>
                                                                                                                                                                                                                                Whitespace : None
                                                                                                                                                                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                                                                                                                                                                          IterAfter  : [2, 18] (32)
                                                                                                                                                                                                                                                                                                                          IterBefore : [2, 17] (31)
                                                                                                                                                                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(31, 32), match='c'>
                                                                                                                                                                                                                                                                                                                          Whitespace : None
                                                                                                                                                                                                                                                                                                        IterAfter  : [2, 18] (32)
                                                                                                                                                                                                                                                                                                        IterBefore : [2, 17] (31)
                                                                                                                                                                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                                                      IterAfter  : [2, 18] (32)
                                                                                                                                                                                                                                                                                      IterBefore : [2, 17] (31)
                                                                                                                                                                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                                                    IterAfter  : [2, 18] (32)
                                                                                                                                                                                                                                                                    IterBefore : [2, 17] (31)
                                                                                                                                                                                                                                                                    Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                                                                  IterAfter  : [2, 18] (32)
                                                                                                                                                                                                                                                  IterBefore : [2, 17] (31)
                                                                                                                                                                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                IterAfter  : [2, 18] (32)
                                                                                                                                                                                                                                IterBefore : [2, 17] (31)
                                                                                                                                                                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                              IterAfter  : [2, 18] (32)
                                                                                                                                                                                                              IterBefore : [2, 16] (30)
                                                                                                                                                                                                              Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [2, 18] (32)
                                                                                                                                                                                            IterBefore : [2, 14] (28)
                                                                                                                                                                                            Type       : Repeat: {Comma and Element, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                                       3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [2, 19] (33)
                                                                                                                                                                                            IterBefore : [2, 18] (32)
                                                                                                                                                                                            Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(32, 33), match=')'>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                          IterAfter  : [2, 19] (33)
                                                                                                                                                                          IterBefore : [2, 12] (26)
                                                                                                                                                                          Type       : Multiple <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [2, 19] (33)
                                                                                                                                                        IterBefore : [2, 12] (26)
                                                                                                                                                        Type       : Tuple Expression <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [2, 19] (33)
                                                                                                                                      IterBefore : [2, 12] (26)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [2, 19] (33)
                                                                                                                    IterBefore : [2, 12] (26)
                                                                                                                    Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [2, 19] (33)
                                                                                                  IterBefore : [2, 7] (21)
                                                                                                  Type       : Suffix <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                IterAfter  : [2, 19] (33)
                                                                                IterBefore : [2, 7] (21)
                                                                                Type       : Repeat: {Suffix, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [3, 1] (34)
                                                                                IterBefore : [2, 19] (33)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 34
                                                                                             Start : 33
                                                                                Whitespace : None
                                                              IterAfter  : [3, 1] (34)
                                                              IterBefore : [2, 1] (15)
                                                              Type       : Yield Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [3, 1] (34)
                                            IterBefore : [2, 1] (15)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [3, 1] (34)
                          IterBefore : [2, 1] (15)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [3, 1] (34)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )
