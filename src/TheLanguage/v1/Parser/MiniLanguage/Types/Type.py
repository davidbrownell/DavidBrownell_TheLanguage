# ----------------------------------------------------------------------
# |
# |  Type.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 21:51:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Type object"""

import os

from typing import Any, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

# TODO: Add alias type

# ----------------------------------------------------------------------
class Type(Interface.Interface, ObjectReprImplBase):
    """\
    Abstract base class for types that can be used at compile time by the compiler.

    Expressions of these types can be used to evaluate constraints or compile time
    conditionals.
    """

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class IsSupportedResult(object):
        result: bool
        refined_type: Optional["Type"]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(self):
        ObjectReprImplBase.__init__(self)

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def name(self) -> str:
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def IsSupportedValue(
        value: Any,
    ) -> bool:
        """Returns True if this Type supports the value"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ToBoolValue(
        value: Any,
    ) -> bool:
        """Converts the value to a boolean value"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def ToStringValue(
        value: Any,
    ) -> str:
        """Converts the value to a string value"""
        return str(value)

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def IsSupportedValueOfType(
        self,
        value: Any,
        query_type: "Type",
    ) -> "Type.IsSupportedResult":
        """\
        Returns True if the value is supported and of the query_type.

        Returns the answer and the result of any type inferencing possible
        based on this information.
        """

        if query_type.__class__ == self.__class__ and self.IsSupportedValue(value):
            return Type.IsSupportedResult(True, self)

        return Type.IsSupportedResult(False, None)

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def IsNotSupportedValueOfType(
        self,
        value: Any,
        query_type: "Type",
    ) -> "Type.IsSupportedResult":
        """\
        Returns True if the value is not supported and of the query_type.

        Returns the answer and the result of any type inferencing possible
        based on this information.
        """

        if query_type.__class__ != self.__class__ or not self.IsSupportedValue(value):
            return Type.IsSupportedResult(True, self)

        return Type.IsSupportedResult(False, None)
