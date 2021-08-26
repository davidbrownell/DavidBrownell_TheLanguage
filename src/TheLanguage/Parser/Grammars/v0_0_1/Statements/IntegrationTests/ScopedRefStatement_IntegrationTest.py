# ----------------------------------------------------------------------
# |
# |  ScopedRefStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-18 16:00:38
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for ScopedRefStatement.py"""

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
    from ..ScopedRefStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_Standard():
    assert Execute(
        textwrap.dedent(
            """\
            with var1 as ref:
                pass

            with var2, as ref:
                pass

            with var3, var4 as ref:
                pass

            with var5, var6, as ref:
                pass

            with (var7) as ref:
                pass

            with (var8, var9, var10) as ref:
                pass

            with (var11, var12, var13,) as ref:
                pass

            with (
                var14,
                var15,
                    var16,
            ) as ref:
                pass
            """,
        ),
    ) == ResultsFromFile()
