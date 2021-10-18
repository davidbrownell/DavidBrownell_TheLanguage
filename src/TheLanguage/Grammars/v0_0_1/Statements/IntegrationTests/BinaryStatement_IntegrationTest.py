# ----------------------------------------------------------------------
# |
# |  BinaryStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 14:11:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for BinaryStatement.py"""

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
    from ..BinaryStatement import *


# ----------------------------------------------------------------------
def test_Mathematical():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 += expr1
            value2 -= expr2
            value3 *= expr3
            value4 **= expr4
            value5 /= expr5
            value6 //= expr6
            value7 %= expr7
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_BitManipulation():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 <<= expr1
            value2 >>= expr2
            value3 ^= expr3
            value4 |= expr4
            value5 &= expr5
            """,
        ),
    )))
