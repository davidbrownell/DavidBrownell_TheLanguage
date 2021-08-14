# ----------------------------------------------------------------------
# |
# |  TransferExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 15:34:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for TransferExpression.py"""

import os
import textwrap

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TransferExpression import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Move():
    assert Execute(
        textwrap.dedent(
            """\
            variable1 = <<move>> foo

            variable2 = <<move>> (a, b, c)
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_Copy():
    assert Execute(
        textwrap.dedent(
            """\
            variable1 = <<copy>> foo

            variable2 = <<copy>> (
                a, b,
            )
            """,
        ),
    ) == ResultsFromFile()
