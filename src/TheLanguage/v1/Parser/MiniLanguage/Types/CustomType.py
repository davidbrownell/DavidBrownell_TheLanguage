# ----------------------------------------------------------------------
# |
# |  CustomType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 21:59:52
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CustomType object"""

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
class CustomType(Type):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
    ):
        super(CustomType, self).__init__()

        self._name                          = name

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def name(self) -> str:
        return self._name

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def IsSupportedValue(
        value: Any,
    ) -> bool:
        return (
            isinstance(value, str)
            and bool(value)
            and not value.startswith('"')
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def ToBoolValue(
        value: Any,
    ) -> bool:
        return True

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def ToStringValue(
        self,
        value: Any,
    ) -> str:
        return value
