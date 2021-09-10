# ----------------------------------------------------------------------
# |
# |  VariableExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 13:18:53
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableExpressionLexerData and VariableExpressionLexerRegions objects"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionLexerInfo import ExpressionLexerData
    from ..Names.NameLexerInfo import NameLexerInfo
    from ...LexerInfo import LexerRegions, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableExpressionLexerData(ExpressionLexerData):
    Name: NameLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableExpressionLexerRegions(LexerRegions):
    Name: Region
