# ----------------------------------------------------------------------
# |
# |  NameLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-09 22:54:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NameLexerData and NameLexerInfo objects"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...LexerInfo import LexerData, LexerInfo, LexerRegions


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NameLexerData(LexerData, Interface.Interface):
    """Abstract base class for all name-related lexer data"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NameLexerInfo(LexerInfo, Interface.Interface):
    """Abstract base class for all name-related lexer info"""

    Data: NameLexerData
    Regions: LexerRegions
