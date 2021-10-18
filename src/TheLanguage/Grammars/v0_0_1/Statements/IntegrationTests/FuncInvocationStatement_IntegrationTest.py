# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-17 19:24:39
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

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..FuncInvocationStatement import *


# ----------------------------------------------------------------------
def test_NoArgs():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Func1()
            obj.Method2()
            a.b.c.d[e].Method3()
            a.b.c.d[e].Method4().Func5()
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_SingleArg():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Func1(arg)

            Func2((a, ))

            Func3(
                argument,
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleArgs():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            Func1(a, b, c)
            Func2(e, InnerFunc(f, g / h), i)
            """,
        ),
    )))
