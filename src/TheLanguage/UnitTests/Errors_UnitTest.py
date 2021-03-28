# ----------------------------------------------------------------------
# |
# |  Errors_UnitTest.py
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
"""Unit test for Errors.py"""

import os
import sys
import textwrap

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

sys.path.insert(0, os.path.join(_script_dir, ".."))
with CallOnExit(lambda: sys.path.pop(0)):
    from Errors import *

# ----------------------------------------------------------------------
class StandardError(Error):
    MessageTemplate                         = Interface.DerivedProperty("This is the message")


# ----------------------------------------------------------------------
def test_StandardError():
    error = StandardError("source", 100, 200)

    assert error.Message == "This is the message"
    assert error.Source == "source"
    assert error.Line == 100
    assert error.Column == 200

# ----------------------------------------------------------------------
def test_CustomException():
    ErrorClass = CreateErrorClass("Values: one={one} two={two}")

    error = ErrorClass(
        "source",
        100,
        200,
        one="ONE",
        two="TWO",
    )

    assert error.Message == "Values: one=ONE two=TWO"
    assert error.Source == "source"
    assert error.Line == 100
    assert error.Column == 200
