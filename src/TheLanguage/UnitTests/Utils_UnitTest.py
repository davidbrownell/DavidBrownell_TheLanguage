# ----------------------------------------------------------------------
# |
# |  Utils_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-28 13:36:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Utils.py"""

import os
import sys

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

sys.path.insert(0, os.path.join(_script_dir, ".."))
with CallOnExit(lambda: sys.path.pop(0)):
    from Utils import *

# ----------------------------------------------------------------------
class TestIsTokenMatch:
    # ----------------------------------------------------------------------
    def test_Start(self):
        assert IsTokenMatch("These are tokens", "These")
        assert IsTokenMatch("These are tokens", "these") == False
        assert IsTokenMatch(
            "These are tokens",
            "These",
            offset=1,
        ) == False

    # ----------------------------------------------------------------------
    def test_Middle(self):
        assert IsTokenMatch("These are tokens", "are") == False
        assert IsTokenMatch(
            "These are tokens",
            "are",
            offset=6,
        )
        assert IsTokenMatch(
            "These are tokens",
            "These",
            offset=7,
        ) == False

    # ----------------------------------------------------------------------
    def test_TokenTooLong(self):
        assert IsTokenMatch("short tokens", "a_very_long_token_greater_than_the_length_of_the_string") == False
