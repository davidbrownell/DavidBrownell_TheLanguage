# ----------------------------------------------------------------------
# |
# |  VariableDeclaration_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 15:44:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for VariableDeclarationStatement.py"""

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
    from ..VariableDeclarationStatement import *
    from ...Common.AutomatedTests import Execute
    from ...Names.VariableName import InvalidNameError


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            one = value
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
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(0, 3), match='one'>
                                                                                                                                      Whitespace : None
                                                                                                                    IterAfter  : [1, 4] (3)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [1, 4] (3)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 4] (3)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 6] (5)
                                                                                IterBefore : [1, 5] (4)
                                                                                Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(4, 5), match='='>
                                                                                Whitespace : 0)   3
                                                                                             1)   4
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [1, 12] (11)
                                                                                                                                                                          IterBefore : [1, 7] (6)
                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(6, 11), match='value'>
                                                                                                                                                                          Whitespace : 0)   5
                                                                                                                                                                                       1)   6
                                                                                                                                                        IterAfter  : [1, 12] (11)
                                                                                                                                                        IterBefore : [1, 7] (6)
                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [1, 12] (11)
                                                                                                                                      IterBefore : [1, 7] (6)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [1, 12] (11)
                                                                                                                    IterBefore : [1, 7] (6)
                                                                                                                    Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [1, 12] (11)
                                                                                                  IterBefore : [1, 7] (6)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 12] (11)
                                                                                IterBefore : [1, 7] (6)
                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [2, 1] (12)
                                                                                IterBefore : [1, 12] (11)
                                                                                Type       : Newline+ <class 'TheLanguage.Parser.Components.Token.NewlineToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.NewlineToken.MatchResult'>
                                                                                             End   : 12
                                                                                             Start : 11
                                                                                Whitespace : None
                                                              IterAfter  : [2, 1] (12)
                                                              IterBefore : [1, 1] (0)
                                                              Type       : Variable Declaration Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (12)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (12)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [2, 1] (12)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_WithModifier():
    assert Execute(
        textwrap.dedent(
            """\
            var one = value
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
                                                                                                                    IterAfter  : [1, 4] (3)
                                                                                                                    IterBefore : [1, 1] (0)
                                                                                                                    Type       : 'var' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                    Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                 Match : <_sre.SRE_Match object; span=(0, 3), match='var'>
                                                                                                                    Whitespace : None
                                                                                                  IterAfter  : [1, 4] (3)
                                                                                                  IterBefore : [1, 1] (0)
                                                                                                  Type       : Modifier <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 4] (3)
                                                                                IterBefore : [1, 1] (0)
                                                                                Type       : Repeat: {Modifier, 0, 1} <class 'TheLanguage.Parser.Phrases.RepeatPhrase.RepeatPhrase'>
                                                                           1)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                      IsIgnored  : False
                                                                                                                                      IterAfter  : [1, 8] (7)
                                                                                                                                      IterBefore : [1, 5] (4)
                                                                                                                                      Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                      Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                   Match : <_sre.SRE_Match object; span=(4, 7), match='one'>
                                                                                                                                      Whitespace : 0)   3
                                                                                                                                                   1)   4
                                                                                                                    IterAfter  : [1, 8] (7)
                                                                                                                    IterBefore : [1, 5] (4)
                                                                                                                    Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                  IterAfter  : [1, 8] (7)
                                                                                                  IterBefore : [1, 5] (4)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 8] (7)
                                                                                IterBefore : [1, 5] (4)
                                                                                Type       : DynamicPhrasesType.Names <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           2)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                IsIgnored  : False
                                                                                IterAfter  : [1, 10] (9)
                                                                                IterBefore : [1, 9] (8)
                                                                                Type       : '=' <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                             Match : <_sre.SRE_Match object; span=(8, 9), match='='>
                                                                                Whitespace : 0)   7
                                                                                             1)   8
                                                                           3)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                  Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                    Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                      Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Node'>
                                                                                                                                                        Children   : 0)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
                                                                                                                                                                          IsIgnored  : False
                                                                                                                                                                          IterAfter  : [1, 16] (15)
                                                                                                                                                                          IterBefore : [1, 11] (10)
                                                                                                                                                                          Type       : <name> <class 'TheLanguage.Parser.Components.Token.RegexToken'>
                                                                                                                                                                          Value      : <class 'TheLanguage.Parser.Components.Token.RegexToken.MatchResult'>
                                                                                                                                                                                       Match : <_sre.SRE_Match object; span=(10, 15), match='value'>
                                                                                                                                                                          Whitespace : 0)   9
                                                                                                                                                                                       1)   10
                                                                                                                                                        IterAfter  : [1, 16] (15)
                                                                                                                                                        IterBefore : [1, 11] (10)
                                                                                                                                                        Type       : Variable Name <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                                                                                                                      IterAfter  : [1, 16] (15)
                                                                                                                                      IterBefore : [1, 11] (10)
                                                                                                                                      Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                                                    IterAfter  : [1, 16] (15)
                                                                                                                    IterBefore : [1, 11] (10)
                                                                                                                    Type       : Variable Expression <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                                                  IterAfter  : [1, 16] (15)
                                                                                                  IterBefore : [1, 11] (10)
                                                                                                  Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                                                                                IterAfter  : [1, 16] (15)
                                                                                IterBefore : [1, 11] (10)
                                                                                Type       : DynamicPhrasesType.Expressions <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
                                                                           4)   <class 'TheLanguage.Parser.Components.AST.Leaf'>
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
                                                              Type       : Variable Declaration Statement <class 'TheLanguage.Parser.Phrases.SequencePhrase.SequencePhrase'>
                                            IterAfter  : [2, 1] (16)
                                            IterBefore : [1, 1] (0)
                                            Type       : 1.0.0 Grammar <class 'TheLanguage.Parser.Phrases.OrPhrase.OrPhrase'>
                          IterAfter  : [2, 1] (16)
                          IterBefore : [1, 1] (0)
                          Type       : Dynamic Phrases <class 'TheLanguage.Parser.Phrases.DynamicPhrase.DynamicPhrase'>
        IterAfter  : [2, 1] (16)
        IterBefore : [1, 1] (0)
        Type       : <None>
        """,
    )

# ----------------------------------------------------------------------
def test_InvalidLeftHandSide():
    with pytest.raises(InvalidNameError) as ex:
        Execute("InvalidName = value")

    ex = ex.value

    assert str(ex) == "'InvalidName' is not a valid variable or parameter name; names must start with a lowercase letter."
    assert ex.Name == "InvalidName"
    assert ex.Line == 1
    assert ex.Column == 1
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)


# ----------------------------------------------------------------------
def test_InvalidRightHandSide():
    with pytest.raises(InvalidNameError) as ex:
        Execute("one = InvalidName")

    ex = ex.value

    assert str(ex) == "'InvalidName' is not a valid variable or parameter name; names must start with a lowercase letter."
    assert ex.Name == "InvalidName"
    assert ex.Line == 1
    assert ex.Column == 7
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)
