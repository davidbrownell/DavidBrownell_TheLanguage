# ----------------------------------------------------------------------
# |
# |  TupleExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 17:04:41
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

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..TupleExpression import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_SingleExpression():
    assert Execute(
        textwrap.dedent(
            """\
            var1 = (a,)

            var2 = ( # Comment 0
                # Comment 1
                a # Comment 2
                , # Comment 3
                # Comment 4
            )
            """,
        ),
    ) == ResultsFromFile()

# ----------------------------------------------------------------------
def test_MultipleExpressions():
    assert Execute(
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

            val6 = ((x, y), z)
            """,
        ),
    ) == ResultsFromFile()
