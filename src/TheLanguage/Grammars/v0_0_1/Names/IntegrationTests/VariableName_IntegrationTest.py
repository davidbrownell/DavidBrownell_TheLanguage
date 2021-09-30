# ----------------------------------------------------------------------
# |
# |  VariableName_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 16:08:10
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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..VariableName import *


# ----------------------------------------------------------------------
def test_Standard():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            one = value
            """,
        ),
    )))
