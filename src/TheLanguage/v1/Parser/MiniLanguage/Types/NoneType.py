# ----------------------------------------------------------------------
# |
# |  NoneType.py
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
"""Contains the NoneType object"""

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
class NoneType(Type):
    name                                    = Interface.DerivedProperty("None")  # type: ignore

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsSupportedValue(
        value: Any,
    ) -> bool:
        return value is None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ToBoolValue(
        value: Any,  # pylint: disable=unused-argument
    ) -> bool:
        return False
