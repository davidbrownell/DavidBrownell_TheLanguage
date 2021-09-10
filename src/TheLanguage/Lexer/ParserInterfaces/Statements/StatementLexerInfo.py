# ----------------------------------------------------------------------
# |
# |  StatementLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-09 23:11:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StatementLexerData and StatementLexerInfo objects"""

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
class StatementLexerData(LexerData, Interface.Interface):
    """Abstract base class for all statement-related lexer data"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StatementLexerInfo(LexerInfo, Interface.Interface):
    """Abstract base class for all statement-related lexer info"""

    Data: StatementLexerData
    Regions: LexerRegions
