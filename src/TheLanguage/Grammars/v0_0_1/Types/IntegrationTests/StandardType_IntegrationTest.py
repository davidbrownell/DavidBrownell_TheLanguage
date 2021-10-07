# ----------------------------------------------------------------------
# |
# |  StandardType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 12:51:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for StandardType.py"""

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
    from ..StandardType import *


# ----------------------------------------------------------------------
@pytest.mark.skip("Enable when Function Declarations are implemented")
def test_NoModifier():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Int Func():
                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
@pytest.mark.skip("Enable when Function Declarations are implemented")
def test_WithModifier():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Int var Func1():
                pass

            Char view Func2():
                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
# TODO: Remove this placeholder once Function Declarations are implemented
def test_Placeholder():
    assert True
