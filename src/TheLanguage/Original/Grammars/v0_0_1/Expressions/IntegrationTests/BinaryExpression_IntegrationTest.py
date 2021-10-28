# ----------------------------------------------------------------------
# |
# |  BinaryExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 19:06:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for BinaryExpression.py"""

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
    from ..BinaryExpression import *


# ----------------------------------------------------------------------
def test_Logical():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = one and two
            var2 = three or four
            var3 = five in six
            var4 = seven is eight
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Comparison():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_FunctionInvocation():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = func1().func2().func3()
            var2 = func4().func5()->func6()

            var3 = (
                funcA()
                    .funcB()
                    .funcC()
            )

            var4 = Type1::Type2::FuncA()
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Mathematical():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = one + two
            var2 = three - four
            var3 = five * six
            var4 = seven ** eight
            var5 = nine / ten
            var6 = eleven // twelve
            var7 = thirteen % fourteen

            var10 = one + two - three
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_BitManipulation():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = one << two
            var2 = three >> four
            var3 = five & six
            var4 = seven | eight
            var5 = nine ^ ten
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Nested():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = one + two + three - four == five
            """,
        ),
    )))
