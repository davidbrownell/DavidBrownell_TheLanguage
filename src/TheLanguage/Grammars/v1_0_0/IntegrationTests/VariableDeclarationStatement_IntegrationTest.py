# ----------------------------------------------------------------------
# |
# |  VariableDeclarationStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 14:34:33
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
    from . import Execute
    from ..VariableDeclarationStatement import *


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            one = two
            three = Four()
            fix = Six(
                seven,
                eight,
                nine=value,
            )
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                    '=' <<Regex: <_sre.SRE_Match object; span=(4, 5), match='='>>> ws:(3, 4) [1, 5 -> 1, 6]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Variable Name
                                <name> <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(10, 15), match='three'>>> ws:None [2, 1 -> 2, 6]
                    '=' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='='>>> ws:(15, 16) [2, 7 -> 2, 8]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Function Invocation
                                <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='Four'>>> ws:(17, 18) [2, 9 -> 2, 13]
                                '(' <<Regex: <_sre.SRE_Match object; span=(22, 23), match='('>>> ws:None [2, 13 -> 2, 14]
                                ')' <<Regex: <_sre.SRE_Match object; span=(23, 24), match=')'>>> ws:None [2, 14 -> 2, 15]
            1.0.0 Grammar
                Variable Declaration
                    <name> <<Regex: <_sre.SRE_Match object; span=(25, 28), match='fix'>>> ws:None [3, 1 -> 3, 4]
                    '=' <<Regex: <_sre.SRE_Match object; span=(29, 30), match='='>>> ws:(28, 29) [3, 5 -> 3, 6]
                    DynamicStatements.Expressions
                        1.0.0 Grammar
                            Function Invocation
                                <name> <<Regex: <_sre.SRE_Match object; span=(31, 34), match='Six'>>> ws:(30, 31) [3, 7 -> 3, 10]
                                '(' <<Regex: <_sre.SRE_Match object; span=(34, 35), match='('>>> ws:None [3, 10 -> 3, 11]
                                Repeat: (Arguments, 0, 1)
                                    Arguments
                                        Or: [Keyword, DynamicStatements.Expressions]
                                            DynamicStatements.Expressions
                                                1.0.0 Grammar
                                                    Variable Name
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(40, 45), match='seven'>>> ws:None [4, 5 -> 4, 10]
                                        Repeat: (Comma and Argument, 0, None)
                                            Comma and Argument
                                                ',' <<Regex: <_sre.SRE_Match object; span=(45, 46), match=','>>> ws:None [4, 10 -> 4, 11]
                                                Or: [Keyword, DynamicStatements.Expressions]
                                                    DynamicStatements.Expressions
                                                        1.0.0 Grammar
                                                            Variable Name
                                                                <name> <<Regex: <_sre.SRE_Match object; span=(51, 56), match='eight'>>> ws:None [5, 5 -> 5, 10]
                                            Comma and Argument
                                                ',' <<Regex: <_sre.SRE_Match object; span=(56, 57), match=','>>> ws:None [5, 10 -> 5, 11]
                                                Or: [Keyword, DynamicStatements.Expressions]
                                                    Keyword
                                                        <name> <<Regex: <_sre.SRE_Match object; span=(62, 66), match='nine'>>> ws:None [6, 5 -> 6, 9]
                                                        '=' <<Regex: <_sre.SRE_Match object; span=(66, 67), match='='>>> ws:None [6, 9 -> 6, 10]
                                                        DynamicStatements.Expressions
                                                            1.0.0 Grammar
                                                                Variable Name
                                                                    <name> <<Regex: <_sre.SRE_Match object; span=(67, 72), match='value'>>> ws:None [6, 10 -> 6, 15]
                                        Repeat: (',', 0, 1)
                                            ',' <<Regex: <_sre.SRE_Match object; span=(72, 73), match=','>>> ws:None [6, 15 -> 6, 16]
                                ')' <<Regex: <_sre.SRE_Match object; span=(74, 75), match=')'>>> ws:None [7, 1 -> 7, 2]
        """,
    )

# ----------------------------------------------------------------------
def test_InvalidNames():
    # Invalid casing
    with pytest.raises(InvalidVariableNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Invalid = rhs
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == textwrap.dedent(
        """\
        'Invalid' is not a valid variable name.

        Variable names must:
            Begin with a lowercase letter
            Contain upper-, lower-, numeric-, or underscore-characters
        """,
    )

    assert ex.VariableName == "Invalid"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 1
    assert ex.ColumnEnd == 8

    # Invalid chars
    with pytest.raises(InvalidVariableNameError) as ex:
        Execute(
            textwrap.dedent(
                """\
                I..d = rhs
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == textwrap.dedent(
        """\
        'I..d' is not a valid variable name.

        Variable names must:
            Begin with a lowercase letter
            Contain upper-, lower-, numeric-, or underscore-characters
        """,
    )

    assert ex.VariableName == "I..d"
    assert ex.Line == 1
    assert ex.LineEnd == 1
    assert ex.Column == 1
    assert ex.ColumnEnd == 5
