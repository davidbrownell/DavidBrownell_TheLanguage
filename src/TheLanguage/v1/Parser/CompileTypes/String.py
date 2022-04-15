# ----------------------------------------------------------------------
# |
# |  String.py
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
"""Contains the String object"""

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
    from .CompileType import CompileType


# ----------------------------------------------------------------------
class String(CompileType):
    name                                    = Interface.DerivedProperty("String")  # type: ignore

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsSupported(
        value: Any,
    ) -> bool:
        return isinstance(value, str)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ToBool(
        value: Any,
    ) -> bool:
        return bool(value)
