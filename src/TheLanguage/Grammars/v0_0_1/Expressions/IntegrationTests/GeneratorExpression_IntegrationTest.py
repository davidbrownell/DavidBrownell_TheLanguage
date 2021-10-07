# ----------------------------------------------------------------------
# |
# |  GeneratorExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 10:23:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for GeneratorExpression.py"""

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
    from ..GeneratorExpression import *


# ----------------------------------------------------------------------
def test_Standard():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            a = value1 for value1 in OneToTen()
            b = AddOne(value2) for value2 in OneToTen()
            c = AddOne(value3) for value3 in OneToTen() if value3 % two
            """,
        ),
    )))
