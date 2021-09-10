# ----------------------------------------------------------------------
# |
# |  FuncInvocationExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-13 20:12:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated test for FuncInvocationExpression.py"""

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
    from ..FuncInvocationExpression import *

    from ...Common.ArgumentsPhraseItem import PositionalAfterKeywordError
    from ...Common.AutomatedTests import Execute


# ----------------------------------------------------------------------
def test_NoArgs():
    CompareResultsFromFile(
        Execute(
            textwrap.dedent(
                """\
                value = Func()
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
                value1 = Func1(arg)
                value2 = Func2((a,))
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
                value1 = Func1(a, b, c)
                value2 = Func2(e, InnerFunc(f, (g, h)), i)
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
                value1 = Func1(a=one, b=two, c=three)

                value2 = Func2(
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
                value = Func(a, b, c=three, dee, e=five)
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "Positional arguments may not appear after keyword arguments."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 29
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == 32
