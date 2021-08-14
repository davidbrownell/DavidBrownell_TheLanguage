# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 16:17:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for FuncInvocationStatement.py"""

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
    from ..FuncInvocationStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_NoArgs():
    assert Execute(
        textwrap.dedent(
            """\
            Func()
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_SingleArg():
    assert Execute(
        textwrap.dedent(
            """\
            Func1(arg)
            Func2((a,))
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_MultipleArgs():
    assert Execute(
        textwrap.dedent(
            """\
            Func1(a, b, c)
            Func2(e, InnerFunc(f, (g, h)), i)
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_WithKeywords():
    assert Execute(
        textwrap.dedent(
            """\
            Func1(a=one, b=two, c=three)

            Func2(
                a,
                b,
                c=three,
                d=four,
            )
            """,
        ),
    ) == ResultsFromFile()

# TODO: keyword before pos
