# ----------------------------------------------------------------------
# |
# |  RaiseStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:39:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for RaiseStatement.py"""

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
    from ..RaiseStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_StandAlone():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                raise
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_WithValue():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                raise foo
                raise (a, b)
                """,
            ),
        ),
    )
