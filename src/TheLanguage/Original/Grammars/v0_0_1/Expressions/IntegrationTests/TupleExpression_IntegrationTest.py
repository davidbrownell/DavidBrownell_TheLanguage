# ----------------------------------------------------------------------
# |
# |  TupleExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 08:35:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TupleExpression.py"""

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
    from ..TupleExpression import *


# ----------------------------------------------------------------------
def test_SingleElement():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = (a,)

            var2 = (                        # Comment 0
                # Comment 1
                a # Comment 2
                , # Comment 3
                # Comment 4
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleElements():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            val1 = (a, b)
            val2 = (c, d, )

            val3 = (e, f, g, h)
            val4 = (i, j, k, l, )

            val5 = (m, n,
                o, p,
                    q,
            r,)
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Nested():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            var1 = ((a,), (b, c,), (d, e, f,))
            """,
        ),
    )))
