# ----------------------------------------------------------------------
# |
# |  VariableName_IntegrationTest.py
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
"""Automated tests for VariableName.py"""

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
    from ..VariableName import *
    from ...Common.AutomatedTests import Execute


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
