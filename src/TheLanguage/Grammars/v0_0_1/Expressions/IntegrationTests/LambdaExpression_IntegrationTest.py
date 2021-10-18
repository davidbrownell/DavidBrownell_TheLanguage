# ----------------------------------------------------------------------
# |
# |  LambdaExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-07 15:45:40
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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..LambdaExpression import *


# ----------------------------------------------------------------------
def test_NoArgs():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var0 = lambda(): one + two

            var1 = lambda(): one + two - three / four

            var2 = lambda (): value

            var3 = Func1(a, lambda (): value, b)

            var4 = Func2(
                lambda(): one / two,
                lambda(): three * four,
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleArgs():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = lambda (Int a1, Bool b1,): value

            var2 = lambda (pos: Int a2, Bool b2, key: Char c2): one + two / three * four
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultilineArgs():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = lambda (
                pos:
                    Int a1,
                    Bool b1,
                key:
                    Char c1,
            ): value

            var2 = Func(
                lambda (
                    key:
                        Double d2,
                ): one + two / three * four,
                b2,
                c2,
            )
            """,
        ),
    )))
