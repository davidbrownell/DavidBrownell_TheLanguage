# ----------------------------------------------------------------------
# |
# |  GeneratorExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 19:18:32
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for GeneratorExpression.py"""

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
    from ..GeneratorExpression import *
    from ...Common.AutomatedTests import ExecuteEx


# ----------------------------------------------------------------------
def test_Standard():
    result, node = ExecuteEx(
        textwrap.dedent(
            """\
            a = value1 for value1 in OneToTen()

            b = AddOne(value2) for value2 in OneToTen()

            c = AddOne(value3) for value3 in OneToTen() if value3 % two
            """,
        ),
    )

    CompareResultsFromFile(result)
