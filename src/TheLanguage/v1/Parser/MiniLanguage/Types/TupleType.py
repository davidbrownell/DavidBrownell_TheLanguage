# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-17 07:51:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

import os

from typing import Any, List

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
class TupleType(Type):
    supported_scope                         = Interface.DerivedProperty(Type.Scope.TypeCustomization)  # type: ignore

    # ----------------------------------------------------------------------
    def __init__(
        self,
        types: List[Type],
    ):
        super(TupleType, self).__init__()

        assert types

        self.types                          = types
        self._name                          = "Tuple({}, )".format(", ".join(the_type.name for the_type in types))

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def name(self) -> str:
        return self._name

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSupportedValue(
        self,
        value: Any,
    ) -> bool:
        return (
            isinstance(value, tuple)
            and len(value) == len(self.types)
            and all(the_type.IsSupportedValue(value) for the_type, value in zip(self.types, value))
        )

    # ----------------------------------------------------------------------
    @staticmethod
    def ToBoolValue(
        value: Any,
    ) -> bool:
        return bool(value)
