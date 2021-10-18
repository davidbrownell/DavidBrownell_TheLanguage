# ----------------------------------------------------------------------
# |
# |  CastExpression_IntegrationTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 09:36:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Automated tests for CastExpression.py"""

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
    from ..CastExpression import *


# ----------------------------------------------------------------------
def test_Standard():
    CompareResultsFromFile(str(Execute(
        textwrap.dedent(
            """\
            value1 = one as Int
            value2 = two as Char
            value3 = three as val
            """,
        ),
    )))


# ----------------------------------------------------------------------
def test_TypeWithModifierError():
    with pytest.raises(TypeWithModifierError) as ex:
        Execute(
            textwrap.dedent(
                """\
                value = one as Int var
                """,
            ),
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == "Cast expressions may specify a type or a modifier, but not both."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 20
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == 23


# ----------------------------------------------------------------------
def test_InvalidModifierError():
    with pytest.raises(InvalidModifierError) as ex:
        Execute(
            textwrap.dedent(
                """\
                value = one as mutable
                """,
            ),
            debug_string_on_exceptions=False,
        )

    ex = ex.value

    assert str(ex) == "'mutable' cannot be used in cast expressions; supported values are 'ref', 'val', 'view'."
    assert ex.Region.Begin.Line == 1
    assert ex.Region.Begin.Column == 16
    assert ex.Region.End.Line == 1
    assert ex.Region.End.Column == 23
