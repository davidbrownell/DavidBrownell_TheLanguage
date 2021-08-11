# ----------------------------------------------------------------------
# |
# |  ReturnStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:07:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for ReturnStatement.py"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ReturnStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_StandAlone():
    assert Execute(
        textwrap.dedent(
            """\
            return
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
                                                                                IterAfter  : [1, 7] (6)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : 'return' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(0, 6), match='return'>
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
                                                              Type       : Return Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (7)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (7)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [2, 1] (7)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )


# ----------------------------------------------------------------------
def test_Value():
    assert Execute(
        textwrap.dedent(
            """\
            return value
            return (a,b)
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
                                                                                IterAfter  : [1, 7] (6)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : 'return' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(0, 6), match='return'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [1, 13] (12)
                                                                                                                                                                                            IterBefore : [1, 8] (7)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(7, 12), match='value'>
                                                                                                                                                                                            Whitespace : 0)   6
                                                                                                                                                                                                         1)   7
                                                                                                                                                                          IterAfter  : [1, 13] (12)
                                                                                                                                                                          IterBefore : [1, 8] (7)
                                                                                                                                                                          Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [1, 13] (12)
                                                                                                                                                        IterBefore : [1, 8] (7)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [1, 13] (12)
                                                                                                                                      IterBefore : [1, 8] (7)
                                                                                                                                      Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                    IterAfter  : [1, 13] (12)
                                                                                                                    IterBefore : [1, 8] (7)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [1, 13] (12)
                                                                                                  IterBefore : [1, 8] (7)
                                                                                                  Type       : Value <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [1, 13] (12)
                                                                                IterBefore : [1, 8] (7)
                                                                                Type       : Repeat: {Value, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (13)
                                                                                IterBefore : [1, 13] (12)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 13
                                                                                             Start : 12
                                                                                Whitespace : None
                                                              IterAfter  : [2, 1] (13)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Return Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (13)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (13)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 7] (19)
                                                                                IterBefore : [2, 1] (13)
                                                                                Type       : 'return' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(13, 19), match='return'>
                                                                                Whitespace : None
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [2, 9] (21)
                                                                                                                                                                          IterBefore : [2, 8] (20)
                                                                                                                                                                          Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(20, 21), match='('>
                                                                                                                                                                          Whitespace : 0)   19
                                                                                                                                                                                       1)   20
                                                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                                                    IterAfter  : [2, 10] (22)
                                                                                                                                                                                                                                                                    IterBefore : [2, 9] (21)
                                                                                                                                                                                                                                                                    Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(21, 22), match='a'>
                                                                                                                                                                                                                                                                    Whitespace : None
                                                                                                                                                                                                                                                  IterAfter  : [2, 10] (22)
                                                                                                                                                                                                                                                  IterBefore : [2, 9] (21)
                                                                                                                                                                                                                                                  Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                IterAfter  : [2, 10] (22)
                                                                                                                                                                                                                                IterBefore : [2, 9] (21)
                                                                                                                                                                                                                                Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                              IterAfter  : [2, 10] (22)
                                                                                                                                                                                                              IterBefore : [2, 9] (21)
                                                                                                                                                                                                              Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                            IterAfter  : [2, 10] (22)
                                                                                                                                                                                            IterBefore : [2, 9] (21)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [2, 10] (22)
                                                                                                                                                                          IterBefore : [2, 9] (21)
                                                                                                                                                                          Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                     2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                              IsIgnored  : False
                                                                                                                                                                                                              IterAfter  : [2, 11] (23)
                                                                                                                                                                                                              IterBefore : [2, 10] (22)
                                                                                                                                                                                                              Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                              Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                           Match : <_sre.SRE_Match object; span=(22, 23), match=','>
                                                                                                                                                                                                              Whitespace : None
                                                                                                                                                                                                         1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                                                        IsIgnored  : False
                                                                                                                                                                                                                                                                                                        IterAfter  : [2, 12] (24)
                                                                                                                                                                                                                                                                                                        IterBefore : [2, 11] (23)
                                                                                                                                                                                                                                                                                                        Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(23, 24), match='b'>
                                                                                                                                                                                                                                                                                                        Whitespace : None
                                                                                                                                                                                                                                                                                      IterAfter  : [2, 12] (24)
                                                                                                                                                                                                                                                                                      IterBefore : [2, 11] (23)
                                                                                                                                                                                                                                                                                      Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                                                                                                    IterAfter  : [2, 12] (24)
                                                                                                                                                                                                                                                                    IterBefore : [2, 11] (23)
                                                                                                                                                                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                                  IterAfter  : [2, 12] (24)
                                                                                                                                                                                                                                                  IterBefore : [2, 11] (23)
                                                                                                                                                                                                                                                  Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                                                                IterAfter  : [2, 12] (24)
                                                                                                                                                                                                                                IterBefore : [2, 11] (23)
                                                                                                                                                                                                                                Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                              IterAfter  : [2, 12] (24)
                                                                                                                                                                                                              IterBefore : [2, 11] (23)
                                                                                                                                                                                                              Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                                            IterAfter  : [2, 12] (24)
                                                                                                                                                                                            IterBefore : [2, 10] (22)
                                                                                                                                                                                            Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                          IterAfter  : [2, 12] (24)
                                                                                                                                                                          IterBefore : [2, 10] (22)
                                                                                                                                                                          Type       : Repeat: {Comma and Element, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                     3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [2, 13] (25)
                                                                                                                                                                          IterBefore : [2, 12] (24)
                                                                                                                                                                          Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(24, 25), match=')'>
                                                                                                                                                                          Whitespace : None
                                                                                                                                                        IterAfter  : [2, 13] (25)
                                                                                                                                                        IterBefore : [2, 8] (20)
                                                                                                                                                        Type       : Multiple <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [2, 13] (25)
                                                                                                                                      IterBefore : [2, 8] (20)
                                                                                                                                      Type       : Tuple Expression <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [2, 13] (25)
                                                                                                                    IterBefore : [2, 8] (20)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [2, 13] (25)
                                                                                                  IterBefore : [2, 8] (20)
                                                                                                  Type       : Value <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [2, 13] (25)
                                                                                IterBefore : [2, 8] (20)
                                                                                Type       : Repeat: {Value, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [3, 1] (26)
                                                                                IterBefore : [2, 13] (25)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 26
                                                                                             Start : 25
                                                                                Whitespace : None
                                                              IterAfter  : [3, 1] (26)
                                                              IterBefore : [2, 1] (13)
                                                              Type       : Return Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [3, 1] (26)
                                            IterBefore : [2, 1] (13)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [3, 1] (26)
                          IterBefore : [2, 1] (13)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [3, 1] (26)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )
