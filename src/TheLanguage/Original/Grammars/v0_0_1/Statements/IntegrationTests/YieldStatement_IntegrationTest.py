# ----------------------------------------------------------------------
# |
# |  YieldStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 09:39:14
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

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..YieldStatement import *


# ----------------------------------------------------------------------
def test_StandAlone():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            yield
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_WithValue():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            yield foo
            yield (value,)
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_From():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            yield from foo
            yield from (a, b, c)
            """,
        ),
    )))
