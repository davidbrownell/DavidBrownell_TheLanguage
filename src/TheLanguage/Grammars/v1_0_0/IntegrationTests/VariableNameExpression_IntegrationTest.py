# ----------------------------------------------------------------------
# |
# |  VariableNameExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 11:26:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for VariableNameExpression.py"""

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
    from ..VariableNameExpression import *


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            one = two
            three = four # comment 1
            # comment 2
            five = six



            seven = eight
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 3), match='one'>>> ws:None [1, 1 -> 1, 4]
                        '=' <<Regex: <_sre.SRE_Match object; span=(4, 5), match='='>>> ws:(3, 4) [1, 5 -> 1, 6]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(6, 9), match='two'>>> ws:(5, 6) [1, 7 -> 1, 10]
                        Newline+ <<9, 10>> ws:None [1, 10 -> 2, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(10, 15), match='three'>>> ws:None [2, 1 -> 2, 6]
                        '=' <<Regex: <_sre.SRE_Match object; span=(16, 17), match='='>>> ws:(15, 16) [2, 7 -> 2, 8]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(18, 22), match='four'>>> ws:(17, 18) [2, 9 -> 2, 13]
                        Newline+ <<34, 35>> ws:None [2, 25 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(47, 51), match='five'>>> ws:None [4, 1 -> 4, 5]
                        '=' <<Regex: <_sre.SRE_Match object; span=(52, 53), match='='>>> ws:(51, 52) [4, 6 -> 4, 7]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(54, 57), match='six'>>> ws:(53, 54) [4, 8 -> 4, 11]
                        Newline+ <<57, 61>> ws:None [4, 11 -> 8, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(61, 66), match='seven'>>> ws:None [8, 1 -> 8, 6]
                        '=' <<Regex: <_sre.SRE_Match object; span=(67, 68), match='='>>> ws:(66, 67) [8, 7 -> 8, 8]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                Variable Name
                                    <name> <<Regex: <_sre.SRE_Match object; span=(69, 74), match='eight'>>> ws:(68, 69) [8, 9 -> 8, 14]
                        Newline+ <<74, 75>> ws:None [8, 14 -> 9, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_InvalidNames():
    for invalid_var in [
        "InvalidUppercase",
        "no.dots",
        "ends_with_double_under__",
    ]:
        with pytest.raises(NamingConventions.InvalidVariableNameError) as ex:
            Execute("var = {}".format(invalid_var))

        ex = ex.value

        expected_value = textwrap.dedent(
            """\
            '{}' is not a valid variable name.

            Variable names must:
                Begin with a lowercase letter
                Contain at least 1 upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores
            """,
        ).format(
            invalid_var,
        )

        assert str(ex) == expected_value, invalid_var
