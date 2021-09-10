# ----------------------------------------------------------------------
# |
# |  BinaryStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-17 22:28:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for BinaryStatement.py"""

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
    from ..BinaryStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Mathematical():
    CompareResultsFromFile(
        Execute(
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
        ),
    )


# ----------------------------------------------------------------------
def test_BitManipulation():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 <<= expr1
                value2 >>= expr2
                value3 ^= expr3
                value4 |= expr4
                value5 &= expr5
                """,
            ),
        ),
    )
