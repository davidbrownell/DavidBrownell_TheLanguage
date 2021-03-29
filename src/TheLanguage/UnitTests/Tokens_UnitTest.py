# ----------------------------------------------------------------------
# |
# |  Tokens_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-28 13:28:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit tests for Tokens.py"""

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
    from Tokens import *

# ----------------------------------------------------------------------
def test_Tokens():
    assert MULTILINE_STRING_TOKEN == '"""'
    assert MULTILINE_STRING_TOKEN_length == 3

    assert COMMENT_TOKEN == "#"
    assert COMMENT_TOKEN_length == 1
