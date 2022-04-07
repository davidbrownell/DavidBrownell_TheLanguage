# ----------------------------------------------------------------------
# |
# |  Location_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-11 15:01:10
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
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
    from ..Location import *


# ----------------------------------------------------------------------
def test_Creation():
    assert Location(1, 2).line == 1
    assert Location(1, 2).column == 2

    with pytest.raises(AssertionError):
        Location(0, 2)
    with pytest.raises(AssertionError):
        Location(1, 0)


# ----------------------------------------------------------------------
def test_ComparisonLine():
    assert Location(1, 2) == Location(1, 2)
    assert Location(1, 2) != Location(3, 4)

    assert Location(1, 2) < Location(2, 3)
    assert Location(1, 2) <= Location(2, 3)
    assert Location(1, 2) <= Location(1, 2)

    assert Location(2, 3) > Location(1, 2)
    assert Location(2, 3) >= Location(1, 2)
    assert Location(2, 3) >= Location(2, 3)


# ----------------------------------------------------------------------
def test_ComparisonColumn():
    assert Location(1, 2) == Location(1, 2)
    assert Location(1, 2) != Location(1, 4)

    assert Location(1, 2) < Location(1, 3)
    assert Location(1, 2) <= Location(1, 3)
    assert Location(1, 2) <= Location(1, 2)

    assert Location(2, 3) > Location(2, 2)
    assert Location(2, 3) >= Location(2, 2)
    assert Location(2, 3) >= Location(2, 3)


# ----------------------------------------------------------------------
def test_Repr():
    assert str(Location(1, 2)) == textwrap.dedent(
        """\
        # <class 'v1.Location.Location'>
        column: 2
        line: 1
        """,
    )
