# ----------------------------------------------------------------------
# |
# |  Boolean.py
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
"""Contains the Boolean object"""

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
class Boolean(CompileType):
    name                                    = Interface.DerivedProperty("Boolean")  # type: ignore

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsSupported(
        value: Any,
    ) -> bool:
        return value is True or value is False

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ToBool(
        value: Any,
    ) -> bool:
        return value
