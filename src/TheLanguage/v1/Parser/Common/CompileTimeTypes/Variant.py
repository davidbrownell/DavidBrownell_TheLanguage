# ----------------------------------------------------------------------
# |
# |  Variant.py
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
"""Contains the Variant object"""

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
    from .CompileTimeType import CompileTimeType


# ----------------------------------------------------------------------
class Variant(CompileTimeType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        types: List[CompileTimeType],
    ):
        assert types

        self.types                          = types
        self._name                          = "Variant({})".format(" | ".join(the_type.name for the_type in self.types))

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def name(self):
        return self._name

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSupported(
        self,
        value: Any,
    ) -> bool:
        for the_type in self.types:
            if the_type.IsSupported(value):
                return True

        return False

    # ----------------------------------------------------------------------
    @Interface.override
    def ToBool(
        self,
        value: Any,
    ) -> bool:
        for the_type in self.types:
            if the_type.IsSupported(value):
                return the_type.ToBool(value)

        assert False, value  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSupportedAndOfType(
        self,
        value: Any,
        query_type: CompileTimeType,
    ) -> Tuple[bool, Optional[CompileTimeType]]:
        query_type_type = type(query_type)

        if self.__class__ == query_type_type:
            return super(Variant, self).IsSupportedAndOfType(value, query_type)

        matched_type: Optional[CompileTimeType] = None

        for the_type in self.types:
            if the_type.__class__ == query_type_type:
                if the_type.IsSupported(value):
                    return True, the_type

                matched_type = the_type
                break

        if matched_type is None:
            return False, None

        remaining_types = [the_type for the_type in self.types if the_type is not matched_type]

        if len(remaining_types) == 1:
            return False, remaining_types[0]

        return False, Variant(remaining_types)

    # ----------------------------------------------------------------------
    @Interface.override
    def IsNotSupportedAndOfType(
        self,
        value: Any,
        query_type: CompileTimeType,
    ) -> Tuple[bool, Optional[CompileTimeType]]:
        query_type_type = type(query_type)

        if self.__class__ == query_type_type:
            return super(Variant, self).IsNotSupportedAndOfType(value, query_type)

        matched_type: Optional[CompileTimeType] = None

        for the_type in self.types:
            if the_type.__class__ == query_type_type:
                if the_type.IsSupported(value):
                    return False, None

                matched_type = the_type
                break

        if matched_type is None:
            return True, self

        remaining_types = [the_type for the_type in self.types if the_type is not matched_type]

        if len(remaining_types) == 1:
            return True, remaining_types[0]

        return True, Variant(remaining_types)
