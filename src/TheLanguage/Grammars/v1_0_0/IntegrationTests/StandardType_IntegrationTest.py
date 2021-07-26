# ----------------------------------------------------------------------
# |
# |  StandardType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-18 13:56:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for StandardType.py"""

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
    from ..StandardType import *


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            value1 = type as Int
            value2 = type as Int var
            value3 = type as Int mutable
            """,
        ),
    ) == textwrap.dedent(
        """\
        <Root>
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(0, 6), match='value1'>>> ws:None [1, 1 -> 1, 7]
                        '=' <<Regex: <_sre.SRE_Match object; span=(7, 8), match='='>>> ws:(6, 7) [1, 8 -> 1, 9]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(9, 13), match='type'>>> ws:(8, 9) [1, 10 -> 1, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(14, 16), match='as'>>> ws:(13, 14) [1, 15 -> 1, 17]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Standard
                                                <name> <<Regex: <_sre.SRE_Match object; span=(17, 20), match='Int'>>> ws:(16, 17) [1, 18 -> 1, 21]
                        Newline+ <<20, 21>> ws:None [1, 21 -> 2, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(21, 27), match='value2'>>> ws:None [2, 1 -> 2, 7]
                        '=' <<Regex: <_sre.SRE_Match object; span=(28, 29), match='='>>> ws:(27, 28) [2, 8 -> 2, 9]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(30, 34), match='type'>>> ws:(29, 30) [2, 10 -> 2, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(35, 37), match='as'>>> ws:(34, 35) [2, 15 -> 2, 17]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Standard
                                                <name> <<Regex: <_sre.SRE_Match object; span=(38, 41), match='Int'>>> ws:(37, 38) [2, 18 -> 2, 21]
                                                Repeat: (Modifier, 0, 1)
                                                    Modifier
                                                        'var' <<Regex: <_sre.SRE_Match object; span=(42, 45), match='var'>>> ws:(41, 42) [2, 22 -> 2, 25]
                        Newline+ <<45, 46>> ws:None [2, 25 -> 3, 1]
            Dynamic Statements
                1.0.0 Grammar
                    Variable Declaration
                        <name> <<Regex: <_sre.SRE_Match object; span=(46, 52), match='value3'>>> ws:None [3, 1 -> 3, 7]
                        '=' <<Regex: <_sre.SRE_Match object; span=(53, 54), match='='>>> ws:(52, 53) [3, 8 -> 3, 9]
                        DynamicStatements.Expressions
                            1.0.0 Grammar
                                As
                                    DynamicStatements.Expressions
                                        1.0.0 Grammar
                                            Variable Name
                                                <name> <<Regex: <_sre.SRE_Match object; span=(55, 59), match='type'>>> ws:(54, 55) [3, 10 -> 3, 14]
                                    'as' <<Regex: <_sre.SRE_Match object; span=(60, 62), match='as'>>> ws:(59, 60) [3, 15 -> 3, 17]
                                    DynamicStatements.Types
                                        1.0.0 Grammar
                                            Standard
                                                <name> <<Regex: <_sre.SRE_Match object; span=(63, 66), match='Int'>>> ws:(62, 63) [3, 18 -> 3, 21]
                                                Repeat: (Modifier, 0, 1)
                                                    Modifier
                                                        'mutable' <<Regex: <_sre.SRE_Match object; span=(67, 74), match='mutable'>>> ws:(66, 67) [3, 22 -> 3, 29]
                        Newline+ <<74, 75>> ws:None [3, 29 -> 4, 1]
        """,
    )

# ----------------------------------------------------------------------
def test_InvalidName():
    for invalid_type in [
        "invalidLowercase",
        "No.Dots",
        "Ends_with_double_under__",
    ]:
        with pytest.raises(NamingConventions.InvalidTypeNameError) as ex:
            Execute("value = var as {}".format(invalid_type))

        ex = ex.value

        expected_value = textwrap.dedent(
            """\
            '{}' is not a valid type name.

            Type names must:
                Begin with an uppercase letter
                Contain at least 2 upper-, lower-, numeric-, or underscore-characters
                Not end with double underscores
            """,
        ).format(
            invalid_type,
        )

        assert str(ex) == expected_value, invalid_type
