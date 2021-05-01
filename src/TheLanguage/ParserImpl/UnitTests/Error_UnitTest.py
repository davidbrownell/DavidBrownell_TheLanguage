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
import textwrap

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface

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

    assert str(error) == "This is the message"
    assert error.Line == 100
    assert error.Column == 200

# ----------------------------------------------------------------------
def test_CustomException():
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ErrorClass(Error):
        one: str
        two: str

        MessageTemplate                     = Interface.DerivedProperty("Values: one={one} two={two}")

    # ----------------------------------------------------------------------

    error = ErrorClass(
        100,
        200,
        one="ONE",
        two="TWO",
    )

    assert str(error) == "Values: one=ONE two=TWO"
    assert error.Line == 100
    assert error.Column == 200

# ----------------------------------------------------------------------
def test_AdditionalArgs():
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ErrorClass(Error):
        one: str

        MessageTemplate                     = Interface.DerivedProperty("Values: one={one}")

    # ----------------------------------------------------------------------

    error = ErrorClass(
        100,
        200,
        one="ONE",
    )

    assert str(error) == "Values: one=ONE"
    assert error.Line == 100
    assert error.Column == 200
    assert error.one == "ONE"

# ----------------------------------------------------------------------
def test_SourceError():
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class MySourceError(SourceError):
        one: str
        two: str

        MessageTemplate                     = Interface.DerivedProperty("Values: one={one} two={two}")

    # ----------------------------------------------------------------------

    error = MySourceError(
        100,
        200,
        "source_name",
        "ONE",
        "TWO",
    )

    assert str(error) == textwrap.dedent(
        """\
        source_name <100, 200>:
          Values: one=ONE two=TWO
        """,
    )

    assert error.Source == "source_name"
    assert error.Line == 100
    assert error.Column == 200
    assert error.one == "ONE"
    assert error.two == "TWO"
