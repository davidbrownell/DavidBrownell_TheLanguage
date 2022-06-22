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
    # ----------------------------------------------------------------------
    def __init__(
        self,
        name: str,
    ):
        super(ExternalType, self).__init__()

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
        raise Exception("This should never be called")

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ToBoolValue(
        value: Any,
    ) -> bool:
        raise Exception("This should never be called")

    # ----------------------------------------------------------------------
    @Interface.override
    def ToStringValue(
        self,
        value: Any,
    ) -> str:
        return self._name
