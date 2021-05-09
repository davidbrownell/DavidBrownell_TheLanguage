# ----------------------------------------------------------------------
# |
# |  Coroutine_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-05 19:07:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Coroutine.py"""

import os

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Coroutine import *

# ----------------------------------------------------------------------
def test_Status():
    assert {val.name for val in Status} == set(["Continue", "Terminate", "Yield"])

# ----------------------------------------------------------------------
def test_Execute():
    # ----------------------------------------------------------------------
    def Generator():
        yield 1
        yield 2
        return 3

    # ----------------------------------------------------------------------

    result, prefixes = Execute(Generator())

    assert result == 3
    assert prefixes == [1, 2]
