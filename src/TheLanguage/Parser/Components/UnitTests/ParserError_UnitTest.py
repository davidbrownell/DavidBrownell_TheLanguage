# ----------------------------------------------------------------------
# |
# |  ParserError_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-07 22:57:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Unit test for ParserError.py"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserError import *

# ----------------------------------------------------------------------
class StandardError(ParserError):
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
    class ErrorClass(ParserError):
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
    class ErrorClass(ParserError):
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
