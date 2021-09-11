# ----------------------------------------------------------------------
# |
# |  TypeLexerInfo.py
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
"""Contains the TypeLexerData and TypeLexerInfo objects"""

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
    from ...LexerInfo import LexerData, LexerInfo, LexerRegions, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeLexerData(LexerData, Interface.Interface):
    """Abstract base class for all type-related lexer data"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeLexerInfo(LexerInfo, Interface.Interface):
    """Abstract base class for all type-related lexer info"""

    Data: TypeLexerData
    Regions: LexerRegions

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def GetTypeModifier() -> Optional[Tuple[TypeModifier, Region]]:
        """Returns information about a TypeModifier associated with the type (if any)"""
        return None
