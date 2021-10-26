# ----------------------------------------------------------------------
# |
# |  IntegerLiteralExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-25 09:49:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for IntegerLiteralExpression.py"""

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
    from ..IntegerLiteralExpression import *


# ----------------------------------------------------------------------
def test_Standard():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = 1
            value2 = 123456

            value3 = -2
            value4 = -234567

            value5 = +3
            value6 = +3456789012
            """,
        ),
    )))
