# ----------------------------------------------------------------------
# |
# |  NumberExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 13:48:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for NumberExpression.py"""

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
    from ..NumberExpression import *


# ----------------------------------------------------------------------
def test_Integer():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            standard = 123

            negative_single_digit = -1
            negative_multiple_digits = -123

            positive_single_digit = +4
            positive_multiple_digits = +123456789
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Decimal():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            standard = 123.456
            negative = -1.2345678
            positive = +987.65
            """,
        ),
    )))
