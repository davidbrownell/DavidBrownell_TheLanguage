# ----------------------------------------------------------------------
# |
# |  TypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-09 22:57:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeParserData and TypeParserInfo objects"""

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
    """Abstract base class for all type-related lexer info"""

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def GetTypeModifier() -> Optional[Tuple[TypeModifier, Region]]:
        """Returns information about a TypeModifier associated with the type (if any)"""
        return None
