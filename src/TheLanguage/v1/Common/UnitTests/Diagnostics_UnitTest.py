# ----------------------------------------------------------------------
# |
# |  Diagnostics_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 11:38:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Diagnostics.py"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Diagnostics import *
    from ..Location import *


# ----------------------------------------------------------------------
MyError                                     = CreateError(
    "Here is the {adj} error",
    adj=str,
)


# ----------------------------------------------------------------------
def test_Standard():
    e = MyError.Create(
        region=Region(Location(1, 2), Location(3, 4)),
        adj="groovy",
    )

    assert str(e) == "Here is the groovy error"
    assert e.region == Region(Location(1, 2), Location(3, 4))
