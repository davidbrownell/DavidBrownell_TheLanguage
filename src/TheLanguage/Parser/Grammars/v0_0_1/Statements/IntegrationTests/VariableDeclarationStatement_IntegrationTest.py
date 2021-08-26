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
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import CompareResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..VariableDeclarationStatement import *
    from ...Common.AutomatedTests import Execute
    from ...Common.TypeModifier import InvalidTypeModifierError
    from ...Names.VariableName import InvalidVariableNameError


# ----------------------------------------------------------------------
def test_Standard():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                one = value
                """,
            ),
        ),
    )

# ----------------------------------------------------------------------
def test_WithModifier():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                var one = value
                """,
            ),
        ),
    )

# ----------------------------------------------------------------------
def test_InvalidLeftHandSide():
    # No modifier
    with pytest.raises(InvalidVariableNameError) as ex:
        Execute("InvalidName = value")

    ex = ex.value

    assert str(ex) == "'InvalidName' is not a valid variable or parameter name; names must start with a lowercase letter."
    assert ex.Name == "InvalidName"
    assert ex.Line == 1
    assert ex.Column == 1
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)

    # With modifier
    with pytest.raises(InvalidVariableNameError) as ex:
        Execute("var InvalidName = value")

    ex = ex.value

    assert str(ex) == "'InvalidName' is not a valid variable or parameter name; names must start with a lowercase letter."
    assert ex.Name == "InvalidName"
    assert ex.Line == 1
    assert ex.Column == 5
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)


# ----------------------------------------------------------------------
def test_InvalidRightHandSide():
    with pytest.raises(InvalidVariableNameError) as ex:
        Execute("one = InvalidName")

    ex = ex.value

    assert str(ex) == "'InvalidName' is not a valid variable or parameter name; names must start with a lowercase letter."
    assert ex.Name == "InvalidName"
    assert ex.Line == 1
    assert ex.Column == 7
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)

# ----------------------------------------------------------------------
def test_InvalidModifier():
    with pytest.raises(InvalidTypeModifierError) as ex:
        Execute("varied one = value")

    ex = ex.value

    assert str(ex) == "The type modifier 'varied' is not valid; values may be 'mutable', 'immutable', 'isolated', 'shared', 'var', 'ref', 'val', 'view'."
    assert ex.Name == "varied"
    assert ex.Line == 1
    assert ex.Column == 1
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)
