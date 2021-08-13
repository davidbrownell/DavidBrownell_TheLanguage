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
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

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
    ) == ResultsFromFile()

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
