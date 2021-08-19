# ----------------------------------------------------------------------
# |
# |  YieldStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 23:15:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for YieldStatement.py"""

import os
import textwrap

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..YieldStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_StandAlone():
    assert Execute(
        textwrap.dedent(
            """\
            yield
            """,
        ),
    ) == ResultsFromFile()

# ----------------------------------------------------------------------
def test_WithValue():
    assert Execute(
        textwrap.dedent(
            """\
            yield foo
            yield (value,)
            """,
        ),
    ) == ResultsFromFile()

# ----------------------------------------------------------------------
def test_From():
    assert Execute(
        textwrap.dedent(
            """\
            yield from foo
            yield from (a,b,c)
            """,
        ),
    ) == ResultsFromFile()
