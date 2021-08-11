# ----------------------------------------------------------------------
# |
# |  FuncType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 15:09:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for FuncType.py"""

import os
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..FuncType import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@pytest.mark.skip("TODO: Types are not supported yet")
def test_NoModifier():
    assert Execute(
        textwrap.dedent(
            """\
            (Int ()) Func():
               pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        TODO
        """,
    )


# ----------------------------------------------------------------------
@pytest.mark.skip("TODO: Types are not supported yet")
def test_WithModifier():
    assert Execute(
        textwrap.dedent(
            """\
            (Int var ()) Func1();
                pass

            (Char view (Int, Bool var, Double)) Func2():
                pass
            """,
        ),
    ) == textwrap.dedent(
        """\
        TODO
        """,
    )


# ----------------------------------------------------------------------
def test_TODO():
    # This is here to get tester passing (it has troubles when all the tests are skipped).
    # Remove this test once the tests above are working.
    assert True
