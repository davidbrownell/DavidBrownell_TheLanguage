# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 16:16:47
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

import os

from typing import Any, List, Optional, Tuple

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Type import Type


# ----------------------------------------------------------------------
class VariantType(Type):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        types: List[Type],
    ):
        assert types

        self.types                          = types
        self._name                          = "VariantType({})".format(" | ".join(the_type.name for the_type in self.types))

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def name(self):
        return self._name

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSupportedValue(
        self,
        value: Any,
    ) -> bool:
        for the_type in self.types:
            if the_type.IsSupportedValue(value):
                return True

        return False

    # ----------------------------------------------------------------------
    @Interface.override
    def ToBoolValue(
        self,
        value: Any,
    ) -> bool:
        # TODO: This should update the type

        for the_type in self.types:
            if the_type.IsSupportedValue(value):
                return the_type.ToBoolValue(value)

        assert False, value  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSupportedValueOfType(
        self,
        value: Any,
        query_type: Type,
    ) -> Tuple[bool, Optional[Type]]:
        query_type_type = type(query_type)

        if self.__class__ == query_type_type:
            return super(VariantType, self).IsSupportedValueOfType(value, query_type)

        matched_type: Optional[Type] = None

        for the_type in self.types:
            if the_type.__class__ == query_type_type:
                if the_type.IsSupportedValue(value):
                    return True, the_type

                matched_type = the_type
                break

        if matched_type is None:
            return False, None

        remaining_types = [the_type for the_type in self.types if the_type is not matched_type]

        if len(remaining_types) == 1:
            return False, remaining_types[0]

        return False, VariantType(remaining_types)

    # ----------------------------------------------------------------------
    @Interface.override
    def IsNotSupportedValueOfType(
        self,
        value: Any,
        query_type: Type,
    ) -> Tuple[bool, Optional[Type]]:
        query_type_type = type(query_type)

        if self.__class__ == query_type_type:
            return super(VariantType, self).IsNotSupportedValueOfType(value, query_type)

        matched_type: Optional[Type] = None

        for the_type in self.types:
            if the_type.__class__ == query_type_type:
                if the_type.IsSupportedValue(value):
                    return False, None

                matched_type = the_type
                break

        if matched_type is None:
            return True, self

        remaining_types = [the_type for the_type in self.types if the_type is not matched_type]

        if len(remaining_types) == 1:
            return True, remaining_types[0]

        return True, VariantType(remaining_types)
