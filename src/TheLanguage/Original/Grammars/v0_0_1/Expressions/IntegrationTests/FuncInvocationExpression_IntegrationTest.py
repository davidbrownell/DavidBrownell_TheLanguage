# ----------------------------------------------------------------------
# |
# |  FuncInvocationExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 08:37:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for FuncInvocationExpression.py"""

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
    from ..FuncInvocationExpression import *
    from ...Common.ArgumentsPhraseItem import PositionalAfterKeywordError


# ----------------------------------------------------------------------
def test_NoArgs():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = Func1()

            value2 = Func2(
            )
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_SingleArg():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = Func1(arg)

            value2 = Func2((a, ))

            value3 = Func3(
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
            value1 = Func1(a, b, c)
            value2 = Func2(e, InnerFunc(f, g / h), i)
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_WithKeywords():
    CompareResultsFromFile(str(Execute(
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
    )))


# ----------------------------------------------------------------------
def test_PositionalAfterKeywordError():
    with pytest.raises(PositionalAfterKeywordError) as ex:
        Execute(
            textwrap.dedent(
                """\
                value = Func(a, b, c=three, dee, e=five)
                """,
            ),
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == "Positional arguments may not appear after keyword arguments."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 29
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == 32
