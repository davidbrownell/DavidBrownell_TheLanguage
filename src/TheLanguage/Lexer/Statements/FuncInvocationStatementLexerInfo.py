# ----------------------------------------------------------------------
# |
# |  FuncInvocationStatementLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-12 15:51:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncInvocationStatementLexerData, FuncInvocationStatementLexerInfo, and FuncInvocationStatementLexerRegions objects"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementLexerInfo import StatementLexerData, StatementLexerInfo
    from ..Common.ArgumentLexerInfo import ArgumentLexerInfo
    from ..LexerInfo import LexerRegions, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncInvocationStatementLexerData(StatementLexerData):
    Name: str
    Arguments: Optional[List[ArgumentLexerInfo]]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncInvocationStatementLexerRegions(LexerRegions):
    Name: Region
    Arguments: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncInvocationStatementLexerInfo(StatementLexerInfo):
    Data: FuncInvocationStatementLexerData
    Regions: FuncInvocationStatementLexerRegions
