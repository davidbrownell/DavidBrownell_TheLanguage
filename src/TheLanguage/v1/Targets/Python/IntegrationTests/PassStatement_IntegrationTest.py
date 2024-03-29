# ----------------------------------------------------------------------
# |
# |  PassStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 11:11:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for pass statements"""

import os
import textwrap

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....IntegrationTestHelpers import *


# ----------------------------------------------------------------------
def test_Simple():
    CompareResultsFromFile(
        ExecutePythonTarget(
            textwrap.dedent(
                """\
                public class MyClass:
                    pass
                """,
            ),
            include_fundamental_types=False,
        ),
        file_ext=".py",
    )
