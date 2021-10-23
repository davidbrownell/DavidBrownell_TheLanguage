# ----------------------------------------------------------------------
# |
# |  NoneExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 11:10:49
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for NoneExpression.py"""

import os
import textwrap

import pytest

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....IntegrationTests import *
    from ..NoneExpression import NoneExpression


# ----------------------------------------------------------------------
def test_Standard():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value = None
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_NoneAsFuncName():
    with pytest.raises(SyntaxInvalidError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int None(a, b, c):
                    pass
                """,
            ),
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == textwrap.dedent(
        """\
        The syntax is not recognized. [1, 5]

        No statements matched this content.
        """,
    )
