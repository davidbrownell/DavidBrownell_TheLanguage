# ----------------------------------------------------------------------
# |
# |  ExpressionLexerInfo.py
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
"""Contains the ExpressionLexerData and ExpressionLexerInfo objects"""

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
class ExpressionLexerData(LexerData, Interface.Interface):
    """Abstract base class for all expression-related lexer data"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ExpressionLexerInfo(LexerInfo, Interface.Interface):
    """Abstract base class for all expression-related lexer info"""

    Data: ExpressionLexerData
    Regions: LexerRegions
