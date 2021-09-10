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
    from ..FuncInvocationStatement import *

    from ...Common.ArgumentsPhraseItem import PositionalAfterKeywordError
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_NoArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Func()
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_SingleArg():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Func1(arg)
                Func2((a,))
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_MultipleArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                Func1(a, b, c)
                Func2(e, InnerFunc(f, (g, h)), i)
                """,
            ),
        ),
    )


# ----------------------------------------------------------------------
def test_WithKeywords():
    CompareResultsFromFile(
        Execute(
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
        ),
    )


# ----------------------------------------------------------------------
def test_PositionalAfterKeywordError():
    with pytest.raises(PositionalAfterKeywordError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Func(a, b, c=three, dee, e=five)
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Positional arguments may not appear after keyword arguments."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 21
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == 24
