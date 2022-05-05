# ----------------------------------------------------------------------
# |
# |  NestedType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-05 15:10:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NestedType object"""

import os

from typing import Any

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
class NestedType(Type):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        left_type: Type,
        right_type: Type,
    ):
        super(NestedType, self).__init__()

        if isinstance(left_type, NestedType):
            left_types = left_type.types
        else:
            left_types = [left_type]

        if isinstance(right_type, NestedType):
            right_types = right_type.types
        else:
            right_types = [right_type]

        types = left_types + right_types
        assert types

        self.types                          = types
        self._name                          = ".".join(the_type.name for the_type in types)

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
        return self.types[-1].IsSupportedValue(value)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ToBoolValue(
        value: Any,
    ) -> bool:
        return True
