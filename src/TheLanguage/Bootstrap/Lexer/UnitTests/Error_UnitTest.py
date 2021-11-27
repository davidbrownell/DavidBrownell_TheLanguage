# ----------------------------------------------------------------------
# |
# |  Error_UnitTest.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-23 17:50:59
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

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Error import *


# ----------------------------------------------------------------------
def test_StandardError():
    # ----------------------------------------------------------------------
    if USE_THE_LANGUAGE_GENERATED_CODE:
        class StandardError(Error):
            @staticmethod
            def _GetMessageTemplate():
                return "This is the message"
    else:
        @dataclass(frozen=True)
        class StandardError(Error):
            MessageTemplate                     = Interface.DerivedProperty(  # type: ignore
                "This is the message",
            )

    # ----------------------------------------------------------------------

    error = StandardError(100, 200)

    assert str(error) == "This is the message"
    assert error.Line == 100
    assert error.Column == 200


# ----------------------------------------------------------------------
def test_CustomError():
    # ----------------------------------------------------------------------
    if USE_THE_LANGUAGE_GENERATED_CODE:
        class CustomError(Error):
            def __init__(self, line, col, one, two):
                super(CustomError, self).__init__(line, col)
                self.one = one
                self.two = two

            @staticmethod
            def _GetMessageTemplate():
                return "Values: one={one}, two={two}"
    else:
        @dataclass(frozen=True)
        class CustomError(Error):
            one: str
            two: str

            MessageTemplate                     = Interface.DerivedProperty(  # type: ignore
                "Values: one={one}, two={two}",
            )

    # ----------------------------------------------------------------------

    error = CustomError(
        100,
        200,
        "ONE",
        "TWO",
    )

    assert str(error) == "Values: one=ONE, two=TWO"
    assert error.Line == 100
    assert error.Column == 200
    assert error.one == "ONE"
    assert error.two == "TWO"
