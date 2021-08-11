# ----------------------------------------------------------------------
# |
# |  FuncDefinitionStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 15:19:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for FuncDefinitionStatement.py"""

import os
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..FuncDefinitionStatement import *
    from ...Common.AutomatedTests import Execute

    from ...Names.VariableName import InvalidNameError
    from ...Types.StandardType import InvalidTypeError


# ----------------------------------------------------------------------
def test_NoArgs():
    assert Execute(
        textwrap.dedent(
            """\
            Int Func1():
                pass

            Int var Func2():
                pass
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
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [1, 4] (3)
                                                                                                                                      IterBefore : [1, 1] (0)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='Int'>
                                                                                                                                      Whitespace : None
                                                                                                                    IterAfter  : [1, 4] (3)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [1, 4] (3)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 4] (3)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 10] (9)
                                                                                IterBefore : [1, 5] (4)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(4, 9), match='Func1'>
                                                                                Whitespace : 0)   3
                                                                                             1)   4
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 11] (10)
                                                                                IterBefore : [1, 10] (9)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(9, 10), match='('>
                                                                                Whitespace : None
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 12] (11)
                                                                                IterBefore : [1, 11] (10)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(10, 11), match=')'>
                                                                                Whitespace : None
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 13] (12)
                                                                                IterBefore : [1, 12] (11)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(11, 12), match=':'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (13)
                                                                                IterBefore : [1, 13] (12)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 13
                                                                                             Start : 12
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 5] (17)
                                                                                IterBefore : [2, 1] (13)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 17
                                                                                             Start : 13
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [2, 9] (21)
                                                                                                                                                        IterBefore : [2, 5] (17)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(17, 21), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [4, 1] (23)
                                                                                                                                                        IterBefore : [2, 9] (21)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 23
                                                                                                                                                                     Start : 21
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [4, 1] (23)
                                                                                                                                      IterBefore : [2, 5] (17)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [4, 1] (23)
                                                                                                                    IterBefore : [2, 5] (17)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [4, 1] (23)
                                                                                                  IterBefore : [2, 5] (17)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [4, 1] (23)
                                                                                IterBefore : [2, 5] (17)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 1] (23)
                                                                                IterBefore : [4, 1] (23)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [4, 1] (23)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [4, 1] (23)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [4, 1] (23)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [4, 4] (26)
                                                                                                                                      IterBefore : [4, 1] (23)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(23, 26), match='Int'>
                                                                                                                                      Whitespace : None
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [4, 8] (30)
                                                                                                                                                                          IterBefore : [4, 5] (27)
                                                                                                                                                                          Type       : 'var' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(27, 30), match='var'>
                                                                                                                                                                          Whitespace : 0)   26
                                                                                                                                                                                       1)   27
                                                                                                                                                        IterAfter  : [4, 8] (30)
                                                                                                                                                        IterBefore : [4, 5] (27)
                                                                                                                                                        Type       : Modifier <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [4, 8] (30)
                                                                                                                                      IterBefore : [4, 5] (27)
                                                                                                                                      Type       : Repeat: {Modifier, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                    IterAfter  : [4, 8] (30)
                                                                                                                    IterBefore : [4, 1] (23)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [4, 8] (30)
                                                                                                  IterBefore : [4, 1] (23)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [4, 8] (30)
                                                                                IterBefore : [4, 1] (23)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 14] (36)
                                                                                IterBefore : [4, 9] (31)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(31, 36), match='Func2'>
                                                                                Whitespace : 0)   30
                                                                                             1)   31
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 15] (37)
                                                                                IterBefore : [4, 14] (36)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(36, 37), match='('>
                                                                                Whitespace : None
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 16] (38)
                                                                                IterBefore : [4, 15] (37)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(37, 38), match=')'>
                                                                                Whitespace : None
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 17] (39)
                                                                                IterBefore : [4, 16] (38)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(38, 39), match=':'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [5, 1] (40)
                                                                                IterBefore : [4, 17] (39)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 40
                                                                                             Start : 39
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [5, 5] (44)
                                                                                IterBefore : [5, 1] (40)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 44
                                                                                             Start : 40
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [5, 9] (48)
                                                                                                                                                        IterBefore : [5, 5] (44)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(44, 48), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [6, 1] (49)
                                                                                                                                                        IterBefore : [5, 9] (48)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 49
                                                                                                                                                                     Start : 48
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [6, 1] (49)
                                                                                                                                      IterBefore : [5, 5] (44)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [6, 1] (49)
                                                                                                                    IterBefore : [5, 5] (44)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [6, 1] (49)
                                                                                                  IterBefore : [5, 5] (44)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [6, 1] (49)
                                                                                IterBefore : [5, 5] (44)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [6, 1] (49)
                                                                                IterBefore : [6, 1] (49)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [6, 1] (49)
                                                              IterBefore : [4, 1] (23)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [6, 1] (49)
                                            IterBefore : [4, 1] (23)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [6, 1] (49)
                          IterBefore : [4, 1] (23)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [6, 1] (49)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_SingleArg():
    assert Execute(
        textwrap.dedent(
            """\
            Int Func1(Bool b):
                pass

            Int var Func2(Bool view b):
                pass
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
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [1, 4] (3)
                                                                                                                                      IterBefore : [1, 1] (0)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='Int'>
                                                                                                                                      Whitespace : None
                                                                                                                    IterAfter  : [1, 4] (3)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [1, 4] (3)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 4] (3)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 10] (9)
                                                                                IterBefore : [1, 5] (4)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(4, 9), match='Func1'>
                                                                                Whitespace : 0)   3
                                                                                             1)   4
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 11] (10)
                                                                                IterBefore : [1, 10] (9)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(9, 10), match='('>
                                                                                Whitespace : None
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [1, 15] (14)
                                                                                                                                                                                            IterBefore : [1, 11] (10)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(10, 14), match='Bool'>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                          IterAfter  : [1, 15] (14)
                                                                                                                                                                          IterBefore : [1, 11] (10)
                                                                                                                                                                          Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [1, 15] (14)
                                                                                                                                                        IterBefore : [1, 11] (10)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [1, 15] (14)
                                                                                                                                      IterBefore : [1, 11] (10)
                                                                                                                                      Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [1, 17] (16)
                                                                                                                                                                                            IterBefore : [1, 16] (15)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(15, 16), match='b'>
                                                                                                                                                                                            Whitespace : 0)   14
                                                                                                                                                                                                         1)   15
                                                                                                                                                                          IterAfter  : [1, 17] (16)
                                                                                                                                                                          IterBefore : [1, 16] (15)
                                                                                                                                                                          Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [1, 17] (16)
                                                                                                                                                        IterBefore : [1, 16] (15)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [1, 17] (16)
                                                                                                                                      IterBefore : [1, 16] (15)
                                                                                                                                      Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                    IterAfter  : [1, 17] (16)
                                                                                                                    IterBefore : [1, 11] (10)
                                                                                                                    Type       : Parameter <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [1, 17] (16)
                                                                                                  IterBefore : [1, 11] (10)
                                                                                                  Type       : Parameters <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                IterAfter  : [1, 17] (16)
                                                                                IterBefore : [1, 11] (10)
                                                                                Type       : Repeat: {Parameters, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 18] (17)
                                                                                IterBefore : [1, 17] (16)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(16, 17), match=')'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 19] (18)
                                                                                IterBefore : [1, 18] (17)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(17, 18), match=':'>
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (19)
                                                                                IterBefore : [1, 19] (18)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 19
                                                                                             Start : 18
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 5] (23)
                                                                                IterBefore : [2, 1] (19)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 23
                                                                                             Start : 19
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [2, 9] (27)
                                                                                                                                                        IterBefore : [2, 5] (23)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(23, 27), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [4, 1] (29)
                                                                                                                                                        IterBefore : [2, 9] (27)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 29
                                                                                                                                                                     Start : 27
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [4, 1] (29)
                                                                                                                                      IterBefore : [2, 5] (23)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [4, 1] (29)
                                                                                                                    IterBefore : [2, 5] (23)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [4, 1] (29)
                                                                                                  IterBefore : [2, 5] (23)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [4, 1] (29)
                                                                                IterBefore : [2, 5] (23)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           9)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 1] (29)
                                                                                IterBefore : [4, 1] (29)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [4, 1] (29)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [4, 1] (29)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [4, 1] (29)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [4, 4] (32)
                                                                                                                                      IterBefore : [4, 1] (29)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(29, 32), match='Int'>
                                                                                                                                      Whitespace : None
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [4, 8] (36)
                                                                                                                                                                          IterBefore : [4, 5] (33)
                                                                                                                                                                          Type       : 'var' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(33, 36), match='var'>
                                                                                                                                                                          Whitespace : 0)   32
                                                                                                                                                                                       1)   33
                                                                                                                                                        IterAfter  : [4, 8] (36)
                                                                                                                                                        IterBefore : [4, 5] (33)
                                                                                                                                                        Type       : Modifier <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [4, 8] (36)
                                                                                                                                      IterBefore : [4, 5] (33)
                                                                                                                                      Type       : Repeat: {Modifier, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                    IterAfter  : [4, 8] (36)
                                                                                                                    IterBefore : [4, 1] (29)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [4, 8] (36)
                                                                                                  IterBefore : [4, 1] (29)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [4, 8] (36)
                                                                                IterBefore : [4, 1] (29)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 14] (42)
                                                                                IterBefore : [4, 9] (37)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(37, 42), match='Func2'>
                                                                                Whitespace : 0)   36
                                                                                             1)   37
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 15] (43)
                                                                                IterBefore : [4, 14] (42)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(42, 43), match='('>
                                                                                Whitespace : None
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [4, 19] (47)
                                                                                                                                                                                            IterBefore : [4, 15] (43)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(43, 47), match='Bool'>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [4, 24] (52)
                                                                                                                                                                                                                                IterBefore : [4, 20] (48)
                                                                                                                                                                                                                                Type       : 'view' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(48, 52), match='view'>
                                                                                                                                                                                                                                Whitespace : 0)   47
                                                                                                                                                                                                                                             1)   48
                                                                                                                                                                                                              IterAfter  : [4, 24] (52)
                                                                                                                                                                                                              IterBefore : [4, 20] (48)
                                                                                                                                                                                                              Type       : Modifier <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                            IterAfter  : [4, 24] (52)
                                                                                                                                                                                            IterBefore : [4, 20] (48)
                                                                                                                                                                                            Type       : Repeat: {Modifier, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                          IterAfter  : [4, 24] (52)
                                                                                                                                                                          IterBefore : [4, 15] (43)
                                                                                                                                                                          Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [4, 24] (52)
                                                                                                                                                        IterBefore : [4, 15] (43)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [4, 24] (52)
                                                                                                                                      IterBefore : [4, 15] (43)
                                                                                                                                      Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [4, 26] (54)
                                                                                                                                                                                            IterBefore : [4, 25] (53)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(53, 54), match='b'>
                                                                                                                                                                                            Whitespace : 0)   52
                                                                                                                                                                                                         1)   53
                                                                                                                                                                          IterAfter  : [4, 26] (54)
                                                                                                                                                                          IterBefore : [4, 25] (53)
                                                                                                                                                                          Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [4, 26] (54)
                                                                                                                                                        IterBefore : [4, 25] (53)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [4, 26] (54)
                                                                                                                                      IterBefore : [4, 25] (53)
                                                                                                                                      Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                    IterAfter  : [4, 26] (54)
                                                                                                                    IterBefore : [4, 15] (43)
                                                                                                                    Type       : Parameter <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [4, 26] (54)
                                                                                                  IterBefore : [4, 15] (43)
                                                                                                  Type       : Parameters <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                IterAfter  : [4, 26] (54)
                                                                                IterBefore : [4, 15] (43)
                                                                                Type       : Repeat: {Parameters, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 27] (55)
                                                                                IterBefore : [4, 26] (54)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(54, 55), match=')'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 28] (56)
                                                                                IterBefore : [4, 27] (55)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(55, 56), match=':'>
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [5, 1] (57)
                                                                                IterBefore : [4, 28] (56)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 57
                                                                                             Start : 56
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [5, 5] (61)
                                                                                IterBefore : [5, 1] (57)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 61
                                                                                             Start : 57
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [5, 9] (65)
                                                                                                                                                        IterBefore : [5, 5] (61)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(61, 65), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [6, 1] (66)
                                                                                                                                                        IterBefore : [5, 9] (65)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 66
                                                                                                                                                                     Start : 65
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [6, 1] (66)
                                                                                                                                      IterBefore : [5, 5] (61)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [6, 1] (66)
                                                                                                                    IterBefore : [5, 5] (61)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [6, 1] (66)
                                                                                                  IterBefore : [5, 5] (61)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [6, 1] (66)
                                                                                IterBefore : [5, 5] (61)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           9)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [6, 1] (66)
                                                                                IterBefore : [6, 1] (66)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [6, 1] (66)
                                                              IterBefore : [4, 1] (29)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [6, 1] (66)
                                            IterBefore : [4, 1] (29)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [6, 1] (66)
                          IterBefore : [4, 1] (29)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [6, 1] (66)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleArgs():
    assert Execute(
        textwrap.dedent(
            """\
            Int Func1(Bool b, Char c, Double d):
                pass

            Int var Func2(Bool var b, Char view c, Double val d):
                pass
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
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [1, 4] (3)
                                                                                                                                      IterBefore : [1, 1] (0)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='Int'>
                                                                                                                                      Whitespace : None
                                                                                                                    IterAfter  : [1, 4] (3)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [1, 4] (3)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 4] (3)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 10] (9)
                                                                                IterBefore : [1, 5] (4)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(4, 9), match='Func1'>
                                                                                Whitespace : 0)   3
                                                                                             1)   4
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 11] (10)
                                                                                IterBefore : [1, 10] (9)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(9, 10), match='('>
                                                                                Whitespace : None
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [1, 15] (14)
                                                                                                                                                                                            IterBefore : [1, 11] (10)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(10, 14), match='Bool'>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                          IterAfter  : [1, 15] (14)
                                                                                                                                                                          IterBefore : [1, 11] (10)
                                                                                                                                                                          Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [1, 15] (14)
                                                                                                                                                        IterBefore : [1, 11] (10)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [1, 15] (14)
                                                                                                                                      IterBefore : [1, 11] (10)
                                                                                                                                      Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [1, 17] (16)
                                                                                                                                                                                            IterBefore : [1, 16] (15)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(15, 16), match='b'>
                                                                                                                                                                                            Whitespace : 0)   14
                                                                                                                                                                                                         1)   15
                                                                                                                                                                          IterAfter  : [1, 17] (16)
                                                                                                                                                                          IterBefore : [1, 16] (15)
                                                                                                                                                                          Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [1, 17] (16)
                                                                                                                                                        IterBefore : [1, 16] (15)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [1, 17] (16)
                                                                                                                                      IterBefore : [1, 16] (15)
                                                                                                                                      Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                    IterAfter  : [1, 17] (16)
                                                                                                                    IterBefore : [1, 11] (10)
                                                                                                                    Type       : Parameter <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [1, 18] (17)
                                                                                                                                                        IterBefore : [1, 17] (16)
                                                                                                                                                        Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(16, 17), match=','>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [1, 23] (22)
                                                                                                                                                                                                                                IterBefore : [1, 19] (18)
                                                                                                                                                                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(18, 22), match='Char'>
                                                                                                                                                                                                                                Whitespace : 0)   17
                                                                                                                                                                                                                                             1)   18
                                                                                                                                                                                                              IterAfter  : [1, 23] (22)
                                                                                                                                                                                                              IterBefore : [1, 19] (18)
                                                                                                                                                                                                              Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [1, 23] (22)
                                                                                                                                                                                            IterBefore : [1, 19] (18)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [1, 23] (22)
                                                                                                                                                                          IterBefore : [1, 19] (18)
                                                                                                                                                                          Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [1, 25] (24)
                                                                                                                                                                                                                                IterBefore : [1, 24] (23)
                                                                                                                                                                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(23, 24), match='c'>
                                                                                                                                                                                                                                Whitespace : 0)   22
                                                                                                                                                                                                                                             1)   23
                                                                                                                                                                                                              IterAfter  : [1, 25] (24)
                                                                                                                                                                                                              IterBefore : [1, 24] (23)
                                                                                                                                                                                                              Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [1, 25] (24)
                                                                                                                                                                                            IterBefore : [1, 24] (23)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [1, 25] (24)
                                                                                                                                                                          IterBefore : [1, 24] (23)
                                                                                                                                                                          Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                        IterAfter  : [1, 25] (24)
                                                                                                                                                        IterBefore : [1, 19] (18)
                                                                                                                                                        Type       : Parameter <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [1, 25] (24)
                                                                                                                                      IterBefore : [1, 17] (16)
                                                                                                                                      Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [1, 26] (25)
                                                                                                                                                        IterBefore : [1, 25] (24)
                                                                                                                                                        Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(24, 25), match=','>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [1, 33] (32)
                                                                                                                                                                                                                                IterBefore : [1, 27] (26)
                                                                                                                                                                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(26, 32), match='Double'>
                                                                                                                                                                                                                                Whitespace : 0)   25
                                                                                                                                                                                                                                             1)   26
                                                                                                                                                                                                              IterAfter  : [1, 33] (32)
                                                                                                                                                                                                              IterBefore : [1, 27] (26)
                                                                                                                                                                                                              Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [1, 33] (32)
                                                                                                                                                                                            IterBefore : [1, 27] (26)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [1, 33] (32)
                                                                                                                                                                          IterBefore : [1, 27] (26)
                                                                                                                                                                          Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [1, 35] (34)
                                                                                                                                                                                                                                IterBefore : [1, 34] (33)
                                                                                                                                                                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(33, 34), match='d'>
                                                                                                                                                                                                                                Whitespace : 0)   32
                                                                                                                                                                                                                                             1)   33
                                                                                                                                                                                                              IterAfter  : [1, 35] (34)
                                                                                                                                                                                                              IterBefore : [1, 34] (33)
                                                                                                                                                                                                              Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [1, 35] (34)
                                                                                                                                                                                            IterBefore : [1, 34] (33)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [1, 35] (34)
                                                                                                                                                                          IterBefore : [1, 34] (33)
                                                                                                                                                                          Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                        IterAfter  : [1, 35] (34)
                                                                                                                                                        IterBefore : [1, 27] (26)
                                                                                                                                                        Type       : Parameter <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [1, 35] (34)
                                                                                                                                      IterBefore : [1, 25] (24)
                                                                                                                                      Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [1, 35] (34)
                                                                                                                    IterBefore : [1, 17] (16)
                                                                                                                    Type       : Repeat: {Comma and Element, 0, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                  IterAfter  : [1, 35] (34)
                                                                                                  IterBefore : [1, 11] (10)
                                                                                                  Type       : Parameters <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                IterAfter  : [1, 35] (34)
                                                                                IterBefore : [1, 11] (10)
                                                                                Type       : Repeat: {Parameters, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 36] (35)
                                                                                IterBefore : [1, 35] (34)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(34, 35), match=')'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 37] (36)
                                                                                IterBefore : [1, 36] (35)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(35, 36), match=':'>
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (37)
                                                                                IterBefore : [1, 37] (36)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 37
                                                                                             Start : 36
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 5] (41)
                                                                                IterBefore : [2, 1] (37)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 41
                                                                                             Start : 37
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [2, 9] (45)
                                                                                                                                                        IterBefore : [2, 5] (41)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(41, 45), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [4, 1] (47)
                                                                                                                                                        IterBefore : [2, 9] (45)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 47
                                                                                                                                                                     Start : 45
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [4, 1] (47)
                                                                                                                                      IterBefore : [2, 5] (41)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [4, 1] (47)
                                                                                                                    IterBefore : [2, 5] (41)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [4, 1] (47)
                                                                                                  IterBefore : [2, 5] (41)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [4, 1] (47)
                                                                                IterBefore : [2, 5] (41)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           9)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 1] (47)
                                                                                IterBefore : [4, 1] (47)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [4, 1] (47)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [4, 1] (47)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [4, 1] (47)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [4, 4] (50)
                                                                                                                                      IterBefore : [4, 1] (47)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(47, 50), match='Int'>
                                                                                                                                      Whitespace : None
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [4, 8] (54)
                                                                                                                                                                          IterBefore : [4, 5] (51)
                                                                                                                                                                          Type       : 'var' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(51, 54), match='var'>
                                                                                                                                                                          Whitespace : 0)   50
                                                                                                                                                                                       1)   51
                                                                                                                                                        IterAfter  : [4, 8] (54)
                                                                                                                                                        IterBefore : [4, 5] (51)
                                                                                                                                                        Type       : Modifier <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [4, 8] (54)
                                                                                                                                      IterBefore : [4, 5] (51)
                                                                                                                                      Type       : Repeat: {Modifier, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                    IterAfter  : [4, 8] (54)
                                                                                                                    IterBefore : [4, 1] (47)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [4, 8] (54)
                                                                                                  IterBefore : [4, 1] (47)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [4, 8] (54)
                                                                                IterBefore : [4, 1] (47)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 14] (60)
                                                                                IterBefore : [4, 9] (55)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(55, 60), match='Func2'>
                                                                                Whitespace : 0)   54
                                                                                             1)   55
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 15] (61)
                                                                                IterBefore : [4, 14] (60)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(60, 61), match='('>
                                                                                Whitespace : None
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [4, 19] (65)
                                                                                                                                                                                            IterBefore : [4, 15] (61)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(61, 65), match='Bool'>
                                                                                                                                                                                            Whitespace : None
                                                                                                                                                                                       1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [4, 23] (69)
                                                                                                                                                                                                                                IterBefore : [4, 20] (66)
                                                                                                                                                                                                                                Type       : 'var' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(66, 69), match='var'>
                                                                                                                                                                                                                                Whitespace : 0)   65
                                                                                                                                                                                                                                             1)   66
                                                                                                                                                                                                              IterAfter  : [4, 23] (69)
                                                                                                                                                                                                              IterBefore : [4, 20] (66)
                                                                                                                                                                                                              Type       : Modifier <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                            IterAfter  : [4, 23] (69)
                                                                                                                                                                                            IterBefore : [4, 20] (66)
                                                                                                                                                                                            Type       : Repeat: {Modifier, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                          IterAfter  : [4, 23] (69)
                                                                                                                                                                          IterBefore : [4, 15] (61)
                                                                                                                                                                          Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [4, 23] (69)
                                                                                                                                                        IterBefore : [4, 15] (61)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [4, 23] (69)
                                                                                                                                      IterBefore : [4, 15] (61)
                                                                                                                                      Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                            IsIgnored  : False
                                                                                                                                                                                            IterAfter  : [4, 25] (71)
                                                                                                                                                                                            IterBefore : [4, 24] (70)
                                                                                                                                                                                            Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                            Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                         Match : <_sre.SRE_Match object; span=(70, 71), match='b'>
                                                                                                                                                                                            Whitespace : 0)   69
                                                                                                                                                                                                         1)   70
                                                                                                                                                                          IterAfter  : [4, 25] (71)
                                                                                                                                                                          IterBefore : [4, 24] (70)
                                                                                                                                                                          Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                        IterAfter  : [4, 25] (71)
                                                                                                                                                        IterBefore : [4, 24] (70)
                                                                                                                                                        Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                      IterAfter  : [4, 25] (71)
                                                                                                                                      IterBefore : [4, 24] (70)
                                                                                                                                      Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                    IterAfter  : [4, 25] (71)
                                                                                                                    IterBefore : [4, 15] (61)
                                                                                                                    Type       : Parameter <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                               1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [4, 26] (72)
                                                                                                                                                        IterBefore : [4, 25] (71)
                                                                                                                                                        Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(71, 72), match=','>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [4, 31] (77)
                                                                                                                                                                                                                                IterBefore : [4, 27] (73)
                                                                                                                                                                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(73, 77), match='Char'>
                                                                                                                                                                                                                                Whitespace : 0)   72
                                                                                                                                                                                                                                             1)   73
                                                                                                                                                                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                                                    IterAfter  : [4, 36] (82)
                                                                                                                                                                                                                                                                    IterBefore : [4, 32] (78)
                                                                                                                                                                                                                                                                    Type       : 'view' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(78, 82), match='view'>
                                                                                                                                                                                                                                                                    Whitespace : 0)   77
                                                                                                                                                                                                                                                                                 1)   78
                                                                                                                                                                                                                                                  IterAfter  : [4, 36] (82)
                                                                                                                                                                                                                                                  IterBefore : [4, 32] (78)
                                                                                                                                                                                                                                                  Type       : Modifier <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                IterAfter  : [4, 36] (82)
                                                                                                                                                                                                                                IterBefore : [4, 32] (78)
                                                                                                                                                                                                                                Type       : Repeat: {Modifier, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                                                              IterAfter  : [4, 36] (82)
                                                                                                                                                                                                              IterBefore : [4, 27] (73)
                                                                                                                                                                                                              Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [4, 36] (82)
                                                                                                                                                                                            IterBefore : [4, 27] (73)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [4, 36] (82)
                                                                                                                                                                          IterBefore : [4, 27] (73)
                                                                                                                                                                          Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [4, 38] (84)
                                                                                                                                                                                                                                IterBefore : [4, 37] (83)
                                                                                                                                                                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(83, 84), match='c'>
                                                                                                                                                                                                                                Whitespace : 0)   82
                                                                                                                                                                                                                                             1)   83
                                                                                                                                                                                                              IterAfter  : [4, 38] (84)
                                                                                                                                                                                                              IterBefore : [4, 37] (83)
                                                                                                                                                                                                              Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [4, 38] (84)
                                                                                                                                                                                            IterBefore : [4, 37] (83)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [4, 38] (84)
                                                                                                                                                                          IterBefore : [4, 37] (83)
                                                                                                                                                                          Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                        IterAfter  : [4, 38] (84)
                                                                                                                                                        IterBefore : [4, 27] (73)
                                                                                                                                                        Type       : Parameter <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [4, 38] (84)
                                                                                                                                      IterBefore : [4, 25] (71)
                                                                                                                                      Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                 1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [4, 39] (85)
                                                                                                                                                        IterBefore : [4, 38] (84)
                                                                                                                                                        Type       : ',' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(84, 85), match=','>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [4, 46] (92)
                                                                                                                                                                                                                                IterBefore : [4, 40] (86)
                                                                                                                                                                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(86, 92), match='Double'>
                                                                                                                                                                                                                                Whitespace : 0)   85
                                                                                                                                                                                                                                             1)   86
                                                                                                                                                                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                                                    IsIgnored  : False
                                                                                                                                                                                                                                                                    IterAfter  : [4, 50] (96)
                                                                                                                                                                                                                                                                    IterBefore : [4, 47] (93)
                                                                                                                                                                                                                                                                    Type       : 'val' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                                                                 Match : <_sre.SRE_Match object; span=(93, 96), match='val'>
                                                                                                                                                                                                                                                                    Whitespace : 0)   92
                                                                                                                                                                                                                                                                                 1)   93
                                                                                                                                                                                                                                                  IterAfter  : [4, 50] (96)
                                                                                                                                                                                                                                                  IterBefore : [4, 47] (93)
                                                                                                                                                                                                                                                  Type       : Modifier <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                                                                                IterAfter  : [4, 50] (96)
                                                                                                                                                                                                                                IterBefore : [4, 47] (93)
                                                                                                                                                                                                                                Type       : Repeat: {Modifier, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                                                                                                                              IterAfter  : [4, 50] (96)
                                                                                                                                                                                                              IterBefore : [4, 40] (86)
                                                                                                                                                                                                              Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [4, 50] (96)
                                                                                                                                                                                            IterBefore : [4, 40] (86)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [4, 50] (96)
                                                                                                                                                                          IterBefore : [4, 40] (86)
                                                                                                                                                                          Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                                                                                IsIgnored  : False
                                                                                                                                                                                                                                IterAfter  : [4, 52] (98)
                                                                                                                                                                                                                                IterBefore : [4, 51] (97)
                                                                                                                                                                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                                                                             Match : <_sre.SRE_Match object; span=(97, 98), match='d'>
                                                                                                                                                                                                                                Whitespace : 0)   96
                                                                                                                                                                                                                                             1)   97
                                                                                                                                                                                                              IterAfter  : [4, 52] (98)
                                                                                                                                                                                                              IterBefore : [4, 51] (97)
                                                                                                                                                                                                              Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                                                                            IterAfter  : [4, 52] (98)
                                                                                                                                                                                            IterBefore : [4, 51] (97)
                                                                                                                                                                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                                                                          IterAfter  : [4, 52] (98)
                                                                                                                                                                          IterBefore : [4, 51] (97)
                                                                                                                                                                          Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                                                                        IterAfter  : [4, 52] (98)
                                                                                                                                                        IterBefore : [4, 40] (86)
                                                                                                                                                        Type       : Parameter <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [4, 52] (98)
                                                                                                                                      IterBefore : [4, 38] (84)
                                                                                                                                      Type       : Comma and Element <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [4, 52] (98)
                                                                                                                    IterBefore : [4, 25] (71)
                                                                                                                    Type       : Repeat: {Comma and Element, 0, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                                                  IterAfter  : [4, 52] (98)
                                                                                                  IterBefore : [4, 15] (61)
                                                                                                  Type       : Parameters <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                IterAfter  : [4, 52] (98)
                                                                                IterBefore : [4, 15] (61)
                                                                                Type       : Repeat: {Parameters, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 53] (99)
                                                                                IterBefore : [4, 52] (98)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(98, 99), match=')'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 54] (100)
                                                                                IterBefore : [4, 53] (99)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(99, 100), match=':'>
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [5, 1] (101)
                                                                                IterBefore : [4, 54] (100)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 101
                                                                                             Start : 100
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [5, 5] (105)
                                                                                IterBefore : [5, 1] (101)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 105
                                                                                             Start : 101
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [5, 9] (109)
                                                                                                                                                        IterBefore : [5, 5] (105)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(105, 109), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [6, 1] (110)
                                                                                                                                                        IterBefore : [5, 9] (109)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 110
                                                                                                                                                                     Start : 109
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [6, 1] (110)
                                                                                                                                      IterBefore : [5, 5] (105)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [6, 1] (110)
                                                                                                                    IterBefore : [5, 5] (105)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [6, 1] (110)
                                                                                                  IterBefore : [5, 5] (105)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [6, 1] (110)
                                                                                IterBefore : [5, 5] (105)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           9)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [6, 1] (110)
                                                                                IterBefore : [6, 1] (110)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [6, 1] (110)
                                                              IterBefore : [4, 1] (47)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [6, 1] (110)
                                            IterBefore : [4, 1] (47)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [6, 1] (110)
                          IterBefore : [4, 1] (47)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [6, 1] (110)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_MultipleStatements():
    assert Execute(
        textwrap.dedent(
            """\
            Int Func():
                pass
                pass

                pass
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
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [1, 4] (3)
                                                                                                                                      IterBefore : [1, 1] (0)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='Int'>
                                                                                                                                      Whitespace : None
                                                                                                                    IterAfter  : [1, 4] (3)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [1, 4] (3)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 4] (3)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 9] (8)
                                                                                IterBefore : [1, 5] (4)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(4, 8), match='Func'>
                                                                                Whitespace : 0)   3
                                                                                             1)   4
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 10] (9)
                                                                                IterBefore : [1, 9] (8)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(8, 9), match='('>
                                                                                Whitespace : None
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 11] (10)
                                                                                IterBefore : [1, 10] (9)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(9, 10), match=')'>
                                                                                Whitespace : None
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 12] (11)
                                                                                IterBefore : [1, 11] (10)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(10, 11), match=':'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (12)
                                                                                IterBefore : [1, 12] (11)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 12
                                                                                             Start : 11
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 5] (16)
                                                                                IterBefore : [2, 1] (12)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 16
                                                                                             Start : 12
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [2, 9] (20)
                                                                                                                                                        IterBefore : [2, 5] (16)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(16, 20), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [3, 1] (21)
                                                                                                                                                        IterBefore : [2, 9] (20)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 21
                                                                                                                                                                     Start : 20
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [3, 1] (21)
                                                                                                                                      IterBefore : [2, 5] (16)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [3, 1] (21)
                                                                                                                    IterBefore : [2, 5] (16)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [3, 1] (21)
                                                                                                  IterBefore : [2, 5] (16)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                             1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [3, 9] (29)
                                                                                                                                                        IterBefore : [3, 5] (25)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(25, 29), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [5, 1] (31)
                                                                                                                                                        IterBefore : [3, 9] (29)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 31
                                                                                                                                                                     Start : 29
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [5, 1] (31)
                                                                                                                                      IterBefore : [3, 5] (25)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [5, 1] (31)
                                                                                                                    IterBefore : [3, 5] (25)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [5, 1] (31)
                                                                                                  IterBefore : [3, 5] (25)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                             2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [5, 9] (39)
                                                                                                                                                        IterBefore : [5, 5] (35)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(35, 39), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [6, 1] (40)
                                                                                                                                                        IterBefore : [5, 9] (39)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 40
                                                                                                                                                                     Start : 39
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [6, 1] (40)
                                                                                                                                      IterBefore : [5, 5] (35)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [6, 1] (40)
                                                                                                                    IterBefore : [5, 5] (35)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [6, 1] (40)
                                                                                                  IterBefore : [5, 5] (35)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [6, 1] (40)
                                                                                IterBefore : [2, 5] (16)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [6, 1] (40)
                                                                                IterBefore : [6, 1] (40)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [6, 1] (40)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [6, 1] (40)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [6, 1] (40)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [6, 1] (40)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_WithVisibility():
    assert Execute(
        textwrap.dedent(
            """\
            public Int Func1():
                pass

            protected Bool Func2():
                pass

            private Char Func3():
                pass
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
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                    IsIgnored  : False
                                                                                                                    IterAfter  : [1, 7] (6)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : 'public' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                 Match : <_sre.SRE_Match object; span=(0, 6), match='public'>
                                                                                                                    Whitespace : None
                                                                                                  IterAfter  : [1, 7] (6)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : Visibility <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 7] (6)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : Repeat: {Visibility, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [1, 11] (10)
                                                                                                                                      IterBefore : [1, 8] (7)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(7, 10), match='Int'>
                                                                                                                                      Whitespace : 0)   6
                                                                                                                                                   1)   7
                                                                                                                    IterAfter  : [1, 11] (10)
                                                                                                                    IterBefore : [1, 8] (7)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [1, 11] (10)
                                                                                                  IterBefore : [1, 8] (7)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 11] (10)
                                                                                IterBefore : [1, 8] (7)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 17] (16)
                                                                                IterBefore : [1, 12] (11)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(11, 16), match='Func1'>
                                                                                Whitespace : 0)   10
                                                                                             1)   11
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 18] (17)
                                                                                IterBefore : [1, 17] (16)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(16, 17), match='('>
                                                                                Whitespace : None
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 19] (18)
                                                                                IterBefore : [1, 18] (17)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(17, 18), match=')'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 20] (19)
                                                                                IterBefore : [1, 19] (18)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(18, 19), match=':'>
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (20)
                                                                                IterBefore : [1, 20] (19)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 20
                                                                                             Start : 19
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 5] (24)
                                                                                IterBefore : [2, 1] (20)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 24
                                                                                             Start : 20
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [2, 9] (28)
                                                                                                                                                        IterBefore : [2, 5] (24)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(24, 28), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [4, 1] (30)
                                                                                                                                                        IterBefore : [2, 9] (28)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 30
                                                                                                                                                                     Start : 28
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [4, 1] (30)
                                                                                                                                      IterBefore : [2, 5] (24)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [4, 1] (30)
                                                                                                                    IterBefore : [2, 5] (24)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [4, 1] (30)
                                                                                                  IterBefore : [2, 5] (24)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [4, 1] (30)
                                                                                IterBefore : [2, 5] (24)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           9)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 1] (30)
                                                                                IterBefore : [4, 1] (30)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [4, 1] (30)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [4, 1] (30)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [4, 1] (30)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                    IsIgnored  : False
                                                                                                                    IterAfter  : [4, 10] (39)
                                                                                                                    IterBefore : [4, 1] (30)
                                                                                                                    Type       : 'protected' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                 Match : <_sre.SRE_Match object; span=(30, 39), match='protected'>
                                                                                                                    Whitespace : None
                                                                                                  IterAfter  : [4, 10] (39)
                                                                                                  IterBefore : [4, 1] (30)
                                                                                                  Type       : Visibility <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [4, 10] (39)
                                                                                IterBefore : [4, 1] (30)
                                                                                Type       : Repeat: {Visibility, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [4, 15] (44)
                                                                                                                                      IterBefore : [4, 11] (40)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(40, 44), match='Bool'>
                                                                                                                                      Whitespace : 0)   39
                                                                                                                                                   1)   40
                                                                                                                    IterAfter  : [4, 15] (44)
                                                                                                                    IterBefore : [4, 11] (40)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [4, 15] (44)
                                                                                                  IterBefore : [4, 11] (40)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [4, 15] (44)
                                                                                IterBefore : [4, 11] (40)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 21] (50)
                                                                                IterBefore : [4, 16] (45)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(45, 50), match='Func2'>
                                                                                Whitespace : 0)   44
                                                                                             1)   45
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 22] (51)
                                                                                IterBefore : [4, 21] (50)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(50, 51), match='('>
                                                                                Whitespace : None
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 23] (52)
                                                                                IterBefore : [4, 22] (51)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(51, 52), match=')'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [4, 24] (53)
                                                                                IterBefore : [4, 23] (52)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(52, 53), match=':'>
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [5, 1] (54)
                                                                                IterBefore : [4, 24] (53)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 54
                                                                                             Start : 53
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [5, 5] (58)
                                                                                IterBefore : [5, 1] (54)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 58
                                                                                             Start : 54
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [5, 9] (62)
                                                                                                                                                        IterBefore : [5, 5] (58)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(58, 62), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [7, 1] (64)
                                                                                                                                                        IterBefore : [5, 9] (62)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 64
                                                                                                                                                                     Start : 62
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [7, 1] (64)
                                                                                                                                      IterBefore : [5, 5] (58)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [7, 1] (64)
                                                                                                                    IterBefore : [5, 5] (58)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [7, 1] (64)
                                                                                                  IterBefore : [5, 5] (58)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [7, 1] (64)
                                                                                IterBefore : [5, 5] (58)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           9)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [7, 1] (64)
                                                                                IterBefore : [7, 1] (64)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [7, 1] (64)
                                                              IterBefore : [4, 1] (30)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [7, 1] (64)
                                            IterBefore : [4, 1] (30)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [7, 1] (64)
                          IterBefore : [4, 1] (30)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                     2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                          Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                            Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                              Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                    IsIgnored  : False
                                                                                                                    IterAfter  : [7, 8] (71)
                                                                                                                    IterBefore : [7, 1] (64)
                                                                                                                    Type       : 'private' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                 Match : <_sre.SRE_Match object; span=(64, 71), match='private'>
                                                                                                                    Whitespace : None
                                                                                                  IterAfter  : [7, 8] (71)
                                                                                                  IterBefore : [7, 1] (64)
                                                                                                  Type       : Visibility <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [7, 8] (71)
                                                                                IterBefore : [7, 1] (64)
                                                                                Type       : Repeat: {Visibility, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [7, 13] (76)
                                                                                                                                      IterBefore : [7, 9] (72)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(72, 76), match='Char'>
                                                                                                                                      Whitespace : 0)   71
                                                                                                                                                   1)   72
                                                                                                                    IterAfter  : [7, 13] (76)
                                                                                                                    IterBefore : [7, 9] (72)
                                                                                                                    Type       : Standard Type <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [7, 13] (76)
                                                                                                  IterBefore : [7, 9] (72)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [7, 13] (76)
                                                                                IterBefore : [7, 9] (72)
                                                                                Type       : DynamicPhrasesType.Types <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [7, 19] (82)
                                                                                IterBefore : [7, 14] (77)
                                                                                Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(77, 82), match='Func3'>
                                                                                Whitespace : 0)   76
                                                                                             1)   77
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [7, 20] (83)
                                                                                IterBefore : [7, 19] (82)
                                                                                Type       : '(' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(82, 83), match='('>
                                                                                Whitespace : None
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [7, 21] (84)
                                                                                IterBefore : [7, 20] (83)
                                                                                Type       : ')' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(83, 84), match=')'>
                                                                                Whitespace : None
                                                                           5)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [7, 22] (85)
                                                                                IterBefore : [7, 21] (84)
                                                                                Type       : ':' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(84, 85), match=':'>
                                                                                Whitespace : None
                                                                           6)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [8, 1] (86)
                                                                                IterBefore : [7, 22] (85)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 86
                                                                                             Start : 85
                                                                                Whitespace : None
                                                                           7)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [8, 5] (90)
                                                                                IterBefore : [8, 1] (86)
                                                                                Type       : Indent <class 'TheLanguage.Parser.Components.Token.IndentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.IndentToken.MatchResult'>
                                                                                             End   : 90
                                                                                             Start : 86
                                                                                             Value : 4
                                                                                Whitespace : None
                                                                           8)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [8, 9] (94)
                                                                                                                                                        IterBefore : [8, 5] (90)
                                                                                                                                                        Type       : 'pass' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                     Match : <_sre.SRE_Match object; span=(90, 94), match='pass'>
                                                                                                                                                        Whitespace : None
                                                                                                                                                   1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                        IsIgnored  : False
                                                                                                                                                        IterAfter  : [9, 1] (95)
                                                                                                                                                        IterBefore : [8, 9] (94)
                                                                                                                                                        Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                                                                                        Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                                                                                                     End   : 95
                                                                                                                                                                     Start : 94
                                                                                                                                                        Whitespace : None
                                                                                                                                      IterAfter  : [9, 1] (95)
                                                                                                                                      IterBefore : [8, 5] (90)
                                                                                                                                      Type       : Pass Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                    IterAfter  : [9, 1] (95)
                                                                                                                    IterBefore : [8, 5] (90)
                                                                                                                    Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                  IterAfter  : [9, 1] (95)
                                                                                                  IterBefore : [8, 5] (90)
                                                                                                  Type       : Statements <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                IterAfter  : [9, 1] (95)
                                                                                IterBefore : [8, 5] (90)
                                                                                Type       : Repeat: {Statements, 1, None} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           9)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [9, 1] (95)
                                                                                IterBefore : [9, 1] (95)
                                                                                Type       : Dedent <class 'TheLanguage.Parser.Components.Token.DedentToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.DedentToken.MatchResult'>
                                                                                             -- empty dict --
                                                                                Whitespace : None
                                                              IterAfter  : [9, 1] (95)
                                                              IterBefore : [7, 1] (64)
                                                              Type       : Func Definition Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [9, 1] (95)
                                            IterBefore : [7, 1] (64)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [9, 1] (95)
                          IterBefore : [7, 1] (64)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [9, 1] (95)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_InvalidFuncName():
    with pytest.raises(InvalidFuncError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int func():
                    pass
                """,
            )
        )

    ex = ex.value

    assert str(ex) == "'func' is not a valid function name; names must start with an uppercase letter and be at least 2 characters."
    assert ex.Name == "func"
    assert ex.Line == 1
    assert ex.Column == 5
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)

# ----------------------------------------------------------------------
def test_InvalidParameterTypeName():
    with pytest.raises(InvalidTypeError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int Func(
                    invalid name,
                ):
                    pass
                """,
            )
        )

    ex = ex.value

    assert str(ex) == "'invalid' is not a valid type name; names must start with an uppercase letter and be at least 2 characters."
    assert ex.Name == "invalid"
    assert ex.Line == 2
    assert ex.Column == 5
    assert ex.LineEnd == 2
    assert ex.ColumnEnd == ex.Column + len(ex.Name)

# ----------------------------------------------------------------------
def test_InvalidParameterName():
    with pytest.raises(InvalidNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int Func(
                    Bool INVALID,
                ):
                    pass
                """,
            )
        )

    ex = ex.value

    assert str(ex) == "'INVALID' is not a valid variable or parameter name; names must start with a lowercase letter."
    assert ex.Name == "INVALID"
    assert ex.Line == 2
    assert ex.Column == 10
    assert ex.LineEnd == 2
    assert ex.ColumnEnd == ex.Column + len(ex.Name)
