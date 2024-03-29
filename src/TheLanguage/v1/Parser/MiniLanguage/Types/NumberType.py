# ----------------------------------------------------------------------
# |
# |  NumberType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 22:12:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NumberType object"""

import os

from typing import Any, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Type import Type
    from .IntegerType import IntegerType


# ----------------------------------------------------------------------
class NumberType(Type):
    name                                    = Interface.DerivedProperty("Num")  # type: ignore

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsSupportedValue(
        value: Any,
    ) -> bool:
        return isinstance(value, float) or IntegerType.IsSupportedValue(value)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ToBoolValue(
        value: Any,
    ) -> bool:
        return value > 0.0

    # ----------------------------------------------------------------------
    @classmethod
    @Interface.override
    def IsSameOrConvertible(
        cls,
        other: Type,
    ) -> Optional[Type.SameOrConvertibleResult]:
        result = super(NumberType, cls).IsSameOrConvertible(other)
        if result is not None:
            return result

        if other.__class__ == IntegerType:
            return Type.SameOrConvertibleResult.Convertible

        return None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ConvertValueOfType(
        value: Any,
        other_type: Type,
    ) -> Any:
        assert other_type.__class__ == IntegerType, other_type
        return float(value)
