# ----------------------------------------------------------------------
# |
# |  TypeAliasStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-30 14:44:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TypeAliasStatement.py"""

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
    from ..TypeAliasStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Standard():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                using SmallInt = Int
                using MyTuple = (Int, Bool, Char)
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_InvalidName():
    with pytest.raises(InvalidTypeError) as ex:
        Execute(
            textwrap.dedent(
                """\
                using invalid = Int
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "'invalid' is not a valid type name; names must start with an uppercase letter and be at least 2 characters."
    assert ex.Name == "invalid"
    assert ex.Line == 1
    assert ex.Column == 7
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)
