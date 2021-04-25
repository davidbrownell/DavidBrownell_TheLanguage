# ----------------------------------------------------------------------
# |
# |  Error_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-27 16:49:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for Error.py"""

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
    from Error import *

# ----------------------------------------------------------------------
class StandardError(Error):
    MessageTemplate                         = Interface.DerivedProperty("This is the message")


# ----------------------------------------------------------------------
def test_StandardError():
    error = StandardError(100, 200)

    assert error.Message == "This is the message"
    assert error.Line == 100
    assert error.Column == 200

# ----------------------------------------------------------------------
def test_CustomException():
    ErrorClass = CreateErrorClass("Values: one={one} two={two}")

    error = ErrorClass(
        100,
        200,
        one="ONE",
        two="TWO",
    )

    assert error.Message == "Values: one=ONE two=TWO"
    assert error.Line == 100
    assert error.Column == 200

# ----------------------------------------------------------------------
def test_AdditionalArgs():
    ErrorClass = CreateErrorClass("Values: one={one}")

    error = ErrorClass(
        100,
        200,
        one="ONE",
        two="TWO",
        three="THREE",
    )

    assert error.Message == "Values: one=ONE"
    assert error.Line == 100
    assert error.Column == 200
    assert error.one == "ONE"
    assert error.two == "TWO"
    assert error.three == "THREE"
