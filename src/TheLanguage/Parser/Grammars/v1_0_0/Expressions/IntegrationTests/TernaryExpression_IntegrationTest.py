# ----------------------------------------------------------------------
# |
# |  TernaryExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 19:32:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TernaryExpression.py"""

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
    from ..TernaryExpression import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
@pytest.mark.skip("TODO: Enabled once FuncInvicationExpression is available")
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            value1 = TrueFunc() if Condition1() else FalseFunc()
            value2 = (a, b, c) if Condition2() else (d,)
            """,
        ),
    ) == ResultsFromFile()


# Remove this function once the function above is unskipped
def test_RemoveMe():
    assert True
