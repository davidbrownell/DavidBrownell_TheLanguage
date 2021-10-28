# ----------------------------------------------------------------------
# |
# |  NoneTypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-27 15:11:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NoneTypeParserInfo object"""

import os

from typing import Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeParserInfo import Region, TypeModifier, TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NoneTypeParserInfo(TypeParserInfo):
    # ----------------------------------------------------------------------
    @Interface.override
    def GetTypeModifier(self) -> Optional[Tuple[TypeModifier, Region]]:
        return None
