# ----------------------------------------------------------------------
# |
# |  CompileTimeType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 16:08:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CompileTimeType object"""

import os

from typing import Any, Optional, Tuple

import CommonEnvironment
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class CompileTimeType(Interface.Interface):
    """\
    Abstract base class for types that can be used at compile time by the compiler.

    Expressions of these types can be used to evaluate constraints or compile time
    conditionals.
    """

    # ----------------------------------------------------------------------
    @Interface.abstractproperty
    def name(self) -> str:
        raise Exception("Abstract property")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def IsSupported(
        value: Any,
    ) -> bool:
        """Returns True if this CompileTimeType supports the value"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ToBool(
        value: Any,
    ) -> bool:
        """Convert the value to a boolean value"""
        raise Exception("Abstract method")  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def IsSupportedAndOfType(
        self,
        value: Any,
        query_type: "CompileTimeType",
    ) -> Tuple[bool, Optional["CompileTimeType"]]:
        """\
        Returns True if the value is supported and of the query_type.

        Returns the answer and the result of any type inferencing possible
        based on this information.
        """

        if query_type.__class__ == self.__class__ and self.IsSupported(value):
            return True, self

        return False, None

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def IsNotSupportedAndOfType(
        self,
        value: Any,
        query_type: "CompileTimeType",
    ) -> Tuple[bool, Optional["CompileTimeType"]]:
        """\
        Returns True if the value is not supported and of the query_type.

        Returns the answer and the result of any type inferencing possible
        based on this information.
        """

        if query_type.__class__ != self.__class__ or not self.IsSupported(value):
            return True, self

        return False, None
