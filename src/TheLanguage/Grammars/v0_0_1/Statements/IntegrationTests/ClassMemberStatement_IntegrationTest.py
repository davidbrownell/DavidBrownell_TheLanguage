# ----------------------------------------------------------------------
# |
# |  ClassMemberStatement_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-02 13:24:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for ClassMemberStatement.py"""

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
    from ..ClassMemberStatement import *
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_TypeName():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int foo
                    Int _bar
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_TypeModifierName():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int val foo
                    Char view _bar
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_TypeNameDefault():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    Int foo = value1
                    Char _bar = value2
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_TypeModifierNameClassModifier():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                mutable class Foo():
                    Int foo immutable
                    Int var _bar mutable
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_TypeNameClassModifierSingleLineAttribute():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    @Member(init=true)
                    Int value1

                    @Member(init=true)
                    @Member(serialize=false)
                    Char var value2
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_TypeNameClassModifierSingleLineAttributes():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    @Member(init=true) @Member(serialize=false) Int value1
                    @Member(serialize=false) Int value2
                    @Member(init=true, comparison=false) Char var value3
                    @Member(comparison=false) Char var value4
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_TypeNameClassModifierMultiLineAttributes():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    @Member(
                        init=true,
                        comparison=false,
                    )
                    Char var value3

                    @Member(
                        init=true,
                            comparison=false,
                    )
                    Char var value4
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_Visibility():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                class Foo():
                    private Char value1
                    protected Char var value2 = rhs1
                    public Char var value3 immutable = rhs2
                """,
            ),
        ),
    )
