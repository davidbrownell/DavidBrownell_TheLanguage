# ----------------------------------------------------------------------
# |
# |  TryCatchStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-29 05:49:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for TryCatchStatement.py"""

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
    from ..TryCatchStatement import *
    from ...Common.AutomatedTests import Execute

    from ...Names.VariableName import InvalidVariableNameError
    from ...Types.StandardType import InvalidTypeError


# ----------------------------------------------------------------------
def test_Simple():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                try:
                    Func1a()
                catch:
                    Func1b()

                try:
                    Func2a()
                    Func2b()
                catch:
                    Func2c()
                    Func2d()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_SingleCatchVar():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                try:
                    Func1a()
                catch Exception ex:
                    Func1b()

                try:
                    Func2a()
                catch (Exception1 | Exception2) ex:
                    Func2b()
                    Func2c()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_SingleCatchVarWithAll():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                try:
                    Func1a()
                catch Exception ex:
                    Func2a()
                catch:
                    Func3a()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleCatchVar():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                try:
                    Func1a()
                catch Exception1 exception:
                    Func1b()
                catch Exception2 ex:
                    Func1c()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleCatchVarWithAll():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                try:
                    Func1a()
                catch Exception1 exception:
                    Func1b()
                catch Exception2 ex:
                    Func1c()
                catch:
                    Func1d()
                """,
            ),
        ),
    )
