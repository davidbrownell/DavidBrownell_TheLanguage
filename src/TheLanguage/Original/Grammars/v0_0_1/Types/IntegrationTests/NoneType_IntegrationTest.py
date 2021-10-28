# ----------------------------------------------------------------------
# |
# |  NoneType_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-27 15:23:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for NoneType.py"""

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
    from ..NoneType import *


# ----------------------------------------------------------------------
def test_Standard():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            None Func1():
                pass

            (Int | None) Func2():
                pass
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_NoneWithModifierError():
    with pytest.raises(NoneWithModifierError) as ex:
        Execute(
            textwrap.dedent(
                """\
                None var Func():
                    pass
                """,
            ),
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == "Modifiers should never be applied to 'None' types."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 6
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == 9
