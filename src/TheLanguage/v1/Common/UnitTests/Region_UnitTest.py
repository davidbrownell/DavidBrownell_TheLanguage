# ----------------------------------------------------------------------
# |
# |  Region_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-11 15:01:50
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
    from ..Region import *


# ----------------------------------------------------------------------
def test_Creation():
    assert Region(Location(1, 2), Location(3, 4)).begin == Location(1, 2)
    assert Region(Location(1, 2), Location(3, 4)).end == Location(3, 4)

    with pytest.raises(AssertionError):
        Region(Location(3, 4), Location(1, 2))
    with pytest.raises(AssertionError):
        Region(Location(3, 4), Location(3, 3))


# ----------------------------------------------------------------------
def test_Compare():
    assert Region(Location(1, 2), Location(3, 4)) == Region(Location(1, 2), Location(3, 4))
    assert Region(Location(1, 2), Location(3, 4)) != Region(Location(10, 20), Location(30, 40))

    assert Region(Location(1, 2), Location(3, 4)) < Region(Location(10, 20), Location(30, 40))
    assert Region(Location(1, 2), Location(30000, 40000)) <= Region(Location(10, 20), Location(30, 40))


# ----------------------------------------------------------------------
def test_In():
    assert Region(Location(1, 2), Location(3, 4)) in Region(Location(1, 2), Location(3, 4))

    assert Region(Location(2, 2), Location(3, 4)) in Region(Location(1, 2), Location(3, 4))
    assert Region(Location(1, 4), Location(3, 4)) in Region(Location(1, 2), Location(3, 4))

    assert Region(Location(1, 2), Location(2, 4)) in Region(Location(1, 2), Location(3, 4))
    assert Region(Location(1, 2), Location(3, 3)) in Region(Location(1, 2), Location(3, 4))


# ----------------------------------------------------------------------
def test_Repr():
    assert str(Region(Location(1, 2), Location(3, 4))) == textwrap.dedent(
        """\
        # <class 'v1.Common.Region.Region'>
        begin: # <class 'v1.Common.Location.Location'>
          column: 2
          line: 1
        end: # <class 'v1.Common.Location.Location'>
          column: 4
          line: 3
        """,
    )
