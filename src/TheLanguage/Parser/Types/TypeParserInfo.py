# ----------------------------------------------------------------------
# |
# |  TypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 10:42:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeParserInfo object"""

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
    from ..Common.TypeModifier import TypeModifier
    from ..ParserInfo import ParserInfo, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeParserInfo(ParserInfo, Interface.Interface):
    """Abstract base class for all type-related ParserInfo objects"""

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def GetTypeModifier() -> Optional[Tuple[TypeModifier, Region]]:
        """Returns information a TypeModifier associated with the type (if any)"""

        # By default, no TypeModifier
        return None
