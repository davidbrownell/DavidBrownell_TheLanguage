# ----------------------------------------------------------------------
# |
# |  BinaryExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 15:50:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for BinaryExpression.py"""

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
    from ..BinaryExpression import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Logical():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                var1 = one and two
                var2 = three or four
                var3 = five in six
                var4 = seven is eight
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Comparison():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                var1 = one < two
                var2 = three <= four
                var3 = six > seven
                var4 = eight >= nine
                var5 = ten == eleven
                var6 = twelve != thirteen
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_FunctionInvocation():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                var1 = func1().func2().func3()
                var2 = func4()->func5()->func6()

                var3 = (
                    funcA()
                        .funcB()
                        .funcC()
                )
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
                var1 = one + two
                var2 = three - four
                var3 = five * six
                var4 = seven ** eight
                var5 = nine / ten
                var6 = eleven // twelve
                var7 = thirteen % fourteen
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
                var1 = one << two
                var2 = three >> four
                var3 = five & six
                var4 = seven | eight
                var5 = nine ^ ten
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Nested():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                var1 = one + two + three - four == five
                """,
            ),
        ),
    )
