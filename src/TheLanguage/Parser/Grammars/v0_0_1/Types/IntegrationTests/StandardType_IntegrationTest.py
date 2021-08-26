# ----------------------------------------------------------------------
# |
# |  StandardType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 13:59:56
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for StandardType.py"""

import os
import textwrap

import pytest
pytest.register_assert_rewrite("CommonEnvironment.AutomatedTestHelpers")

import CommonEnvironment
from CommonEnvironment.AutomatedTestHelpers import ResultsFromFile

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..StandardType import *
    from ...Common.AutomatedTests import Execute
    from ...Common.TypeModifier import InvalidTypeModifierError

# ----------------------------------------------------------------------
def test_NoModifier():
    assert Execute(
        textwrap.dedent(
            """\
            Int Func():
                pass
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_WithModifier():
    assert Execute(
        textwrap.dedent(
            """\
            Int var Func1():
                pass

            Char view Func2():
                pass
            """,
        ),
    ) == ResultsFromFile()


# ----------------------------------------------------------------------
def test_InvalidModifier():
    with pytest.raises(InvalidTypeModifierError) as ex:
        Execute(
            textwrap.dedent(
                """\
                Int varied Func():
                    pass
                """,
            ),
        )

    ex = ex.value

    assert str(ex) == "The type modifier 'varied' is not valid; values may be 'mutable', 'immutable', 'isolated', 'shared', 'var', 'ref', 'val', 'view'."
    assert ex.Name == "varied"
    assert ex.Line == 1
    assert ex.Column == 5
    assert ex.LineEnd == 1
    assert ex.ColumnEnd == ex.Column + len(ex.Name)
