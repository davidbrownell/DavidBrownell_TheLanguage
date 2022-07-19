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

from enum import auto, Enum
from typing import Any, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

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
    class SameOrConvertibleResult(Enum):
        Same                                = auto()
        Convertible                         = auto()

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
    def __eq__(
        self,
        other: "Type",
    ) -> bool:
        return self.name == other.name

    # ----------------------------------------------------------------------
    def __ne__(
        self,
        other: "Type",
    ) -> bool:
        return not self.__eq__(other)

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
    @classmethod
    @Interface.extensionmethod
    def IsSameOrConvertible(
        cls,
        other: "Type",
    ) -> Optional["Type.SameOrConvertibleResult"]:
        # By default, check the class to see if the other type is the same. Derived
        # Types can provide more exotic behavior if applicable.
        if other.__class__ == cls:
            return Type.SameOrConvertibleResult.Same

        return None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def ConvertValueOfType(
        value: Any,                         # pylint: disable=unused-argument
        other_type: "Type",                 # pylint: disable=unused-argument
    ) -> Any:
        """Converts the value from the other type to a value of the current type"""

        # Convertible types are not supported by default
        raise Exception("Not supported by default")  # pragma: no cover

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

        if self.IsSameOrConvertible(query_type) and self.IsSupportedValue(value):
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

        if not self.IsSameOrConvertible(query_type) or not self.IsSupportedValue(value):
            return Type.IsSupportedResult(True, self)

        return Type.IsSupportedResult(False, None)
