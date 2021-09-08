# ----------------------------------------------------------------------
# |
# |  TupleName_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 22:12:21
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TupleName"""

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
    from ..TupleName import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Single():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                (a,) = value1
                (b,) = value2

                ( # Comment 1
                  b # Comment 2
                ,) = value3
                """,
            ),
        ),
    )

# ----------------------------------------------------------------------
def test_Multiple():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                (a, (b, c), d,) = value
                """,
            ),
        ),
    )