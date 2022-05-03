# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 22:17:12
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

from collections import OrderedDict
from typing import Any, Dict, List, Optional

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
        super(VariantType, self).__init__()

        assert types

        self.types                          = self.__class__._Flatten(types)  # pylint: disable=protected-access
        self._name                          = "Variant({})".format(" | ".join(the_type.name for the_type in types))

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def name(self):
        return self._name

    # ----------------------------------------------------------------------
    def __contains__(
        self,
        query_type: Type,
    ) -> bool:
        return any(query_type.name == the_type.name for the_type in self.types)

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
    @Interface.abstractmethod
    def ToBoolValue(
        self,
        value: Any,
    ) -> bool:
        for the_type in self.types:
            if the_type.IsSupportedValue(value):
                return the_type.ToBoolValue(value)

        assert False, value  # pragma: no cover
        return False

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSupportedValueOfType(
        self,
        value: Any,
        query_type: Type,
    ) -> Type.IsSupportedResult:
        query_type_type = type(query_type)

        if self.__class__ == query_type_type:
            return super(VariantType, self).IsSupportedValueOfType(value, query_type)

        matched_type: Optional[Type] = None

        for the_type in self.types:
            if the_type.__class__ == query_type_type:
                if the_type.IsSupportedValue(value):
                    return Type.IsSupportedResult(True, the_type)

                matched_type = the_type
                break

        if matched_type is None:
            return Type.IsSupportedResult(False, None)

        remaining_types = [the_type for the_type in self.types if the_type is not matched_type]

        if len(remaining_types) == 1:
            return Type.IsSupportedResult(False, remaining_types[0])

        return Type.IsSupportedResult(False, VariantType(remaining_types))

    # ----------------------------------------------------------------------
    @Interface.override
    def IsNotSupportedValueOfType(
        self,
        value: Any,
        query_type: Type,
    ) -> Type.IsSupportedResult:
        query_type_type = type(query_type)

        if self.__class__ == query_type_type:
            return super(VariantType, self).IsNotSupportedValueOfType(value, query_type)

        matched_type: Optional[Type] = None

        for the_type in self.types:
            if the_type.__class__ == query_type_type:
                if the_type.IsSupportedValue(value):
                    return Type.IsSupportedResult(False, None)

                matched_type = the_type
                break

        if matched_type is None:
            return Type.IsSupportedResult(True, self)

        remaining_types = [the_type for the_type in self.types if the_type is not matched_type]

        if len(remaining_types) == 1:
            return Type.IsSupportedResult(True, remaining_types[0])

        return Type.IsSupportedResult(True, VariantType(remaining_types))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _Flatten(
        cls,
        types: List[Type],
    ) -> List[Type]:
        results: Dict[str, Type] = OrderedDict()

        for the_type in types:
            if isinstance(the_type, cls):
                the_types = cls._Flatten(the_type.types)
            else:
                the_types = [the_type, ]

            for typ in the_types:
                if typ.name not in results:
                    results[typ.name] = typ

        return list(results.values())
