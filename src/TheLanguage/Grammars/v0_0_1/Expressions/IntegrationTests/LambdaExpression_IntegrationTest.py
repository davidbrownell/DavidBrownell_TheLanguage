# ----------------------------------------------------------------------
# |
# |  LambdaExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-28 11:37:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for LambdaExpression.py"""

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
    from ..LambdaExpression import *
    from ...Common.AutomatedTests import Execute

# ----------------------------------------------------------------------
def test_NoArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                var1 = lambda (): value

                var2 = Func1(a, lambda (): value, b)

                var3 = Func2(
                    lambda (): true if condition else false,
                    lambda (): one + two,
                )
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                var1 = lambda (Int a, Bool b,): (a, b)

                var2 = lambda (pos: Int a, Bool b, key: Char c): value
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultilineArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                var1 = lambda (
                    pos:
                        Int a,
                        Bool b,
                    key:
                        Char c,
                ): (a, b, c)

                var2 = Func(
                    lambda (
                        key:
                            Double d,
                    ): value2,
                    b,
                    c,
                )
                """,
            ),
        ),
    )
