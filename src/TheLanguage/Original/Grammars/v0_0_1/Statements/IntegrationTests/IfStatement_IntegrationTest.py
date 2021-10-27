# ----------------------------------------------------------------------
# |
# |  IfStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 16:40:31
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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..IfStatement import *


# ----------------------------------------------------------------------
def test_IfOnly():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            if cond1:
                value1a = one_a

            if cond2:
                value2a = two_a
                value2b = two_b

                value2c = two_c
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_IfWithElse():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            if cond1:
                value1a = one_a
            else:
                value1b = one_b

            if cond2:
                value2a = two_a
                value2b = two_b
            else:
                value2c = two_c

                value2d = two_d
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_IfWithElif():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            if cond1:
                value1a = one_a
            elif cond2:
                value2a = two_a

            if cond2:
                value3a = three_a
                value3b = three_b

            elif cond3:
                value3c = three_c
                value3d = three_d
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_IfWithMultipleElif():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            if cond1:
                value1a = one_a
            elif cond2:
                value2a = two_a
            elif cond3:
                value3a = three_a
                value3b = three_b
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Complex():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            if Condition1() and Condition2():
                value1a = one_a

                # Comment 1
                pass

            elif cond3:
                value2a = two_a
                value2b = two_b

                if nested_cond1:
                    value2c = two_c
                else:
                    value2d = two_d

                value2e = two_e

            elif cond4:
                value3a = three_a

            else:
                pass
            """,
        ),
    )))
