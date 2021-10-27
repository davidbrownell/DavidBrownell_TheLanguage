# ----------------------------------------------------------------------
# |
# |  TryStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 11:39:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for TryStatement.py"""

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
    from ..TryStatement import *


# ----------------------------------------------------------------------
def test_Simple():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            try:
                value1a = foo
            except:
                value1b = foo

            try:
                value2a = foo
                value2b = foo
            except:
                value2c = foo
                value2d = foo
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_SingleExceptVar():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            try:
                value1a = foo
            except Exception ex:
                value1b = foo

            try:
                value2a = foo
            except (Exception1 | Exception2) ex:
                value2b = foo
                value2c = foo
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_SingleExceptVarWithAll():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            try:
                value1a = foo
            except Exception ex:
                value2a = foo
            except:
                value3a = foo
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleExceptVar():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            try:
                value1a = foo
            except Exception1 exception:
                value1b = foo
            except Exception2 ex:
                value1c = foo
            except Exception3:
                value1d = foo
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_MultipleExceptVarWithAll():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            try:
                value1a = foo
            except Exception1 exception:
                value1b = foo
            except Exception2 ex:
                value1c = foo
            except:
                value1d = foo
            """,
        ),
    )))
