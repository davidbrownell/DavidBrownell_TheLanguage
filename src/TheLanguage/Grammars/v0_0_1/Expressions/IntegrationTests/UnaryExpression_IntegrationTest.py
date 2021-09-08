# ----------------------------------------------------------------------
# |
# |  UnaryExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 11:51:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for UnaryExpression.py"""

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
    from ..UnaryExpression import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Logical():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = not foo
                value2 = not (a, b, c)
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Transfer():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = copy foo
                value2 = copy (a, b, c)

                value3 = move bar
                value4 = move (e, f,)
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Mathematical():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value1 = +foo
                value2 = +(a, b, c)

                value3 = -bar
                value4 = -(d,)
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
                value1 = ~foo
                value2 = ~(a, b, c)
                """,
            ),
        ),
    )