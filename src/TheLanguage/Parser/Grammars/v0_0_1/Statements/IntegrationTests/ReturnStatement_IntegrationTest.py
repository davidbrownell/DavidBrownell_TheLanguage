# ----------------------------------------------------------------------
# |
# |  ReturnStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:07:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for ReturnStatement.py"""

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
    from ..ReturnStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_StandAlone():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                return
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Value():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                return value
                return (a,b)
                """,
            ),
        ),
    )
