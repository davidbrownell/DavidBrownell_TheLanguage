# ----------------------------------------------------------------------
# |
# |  ExternalType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-17 09:14:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ExternalType object"""

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
class ExternalType(Type):
    supported_scope                         = Interface.DerivedProperty(Type.Scope.TypeCustomization)  # type: ignore

    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
    ):
        self._name                          = name

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
        return isinstance(value, str) and value == self._name

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ToBoolValue(
        value: Any,
    ) -> bool:
        return True

    # ----------------------------------------------------------------------
    @Interface.override
    def ToStringValue(
        value: Any,
    ) -> str:
        return value
