# ----------------------------------------------------------------------
# |
# |  UnaryExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-11 17:18:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for UnaryExpression.py"""

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
    from ..UnaryExpression import *


# ----------------------------------------------------------------------
def test_Async():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = await foo
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Transfer():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = copy foo
            value2 = move bar
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Logical():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = not foo
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_Mathematical():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = +foo
            value2 = -bar
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_BitManipulation():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = ~foo
            """,
        ),
    )))
