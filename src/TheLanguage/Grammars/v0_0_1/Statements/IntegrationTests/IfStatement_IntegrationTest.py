# ----------------------------------------------------------------------
# |
# |  IfStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-28 21:55:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for IfStatement.py"""

import os
import textwrap

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import CompareResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..IfStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_IfOnly():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                if  cond1:
                    Func1a()

                if cond2:
                    Func2a()
                    Func2b()

                    Func2c()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_IfWithElse():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                if cond1:
                    Func1a()
                else:
                    Func1b()

                if cond2:
                    Func2a()
                    Func2b()
                else:
                    Func2c()

                    Func2d()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_IfWithElif():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                if cond1:
                    Func1a()
                elif cond2:
                    Func2a()

                if cond2:
                    Func3a()
                    Func3b()

                elif cond3:
                    Func3c()
                    Func3d()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_IfWithMultipleElif():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                if cond1:
                    Func1a()
                elif cond2:
                    Func2a()
                elif cond3:
                    Func3a()
                    Func3b()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Complex():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                if Condition1() and Condition2():
                    Func1a()

                    # Comment 1
                    pass

                elif cond3:
                    Func2a()
                    Func2b()

                    if nested_cond1:
                        Func2c()
                    else:
                        Func2d()

                    Func2e()

                elif cond4:
                    Func3a()

                else:
                    pass
                """,
            ),
        ),
    )
