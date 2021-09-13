# ----------------------------------------------------------------------
# |
# |  ParametersLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-13 15:22:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the types that interact with parameters"""

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
    from ..LexerInfo import LexerData, LexerInfo, LexerRegions, Region
    from ..Expressions.ExpressionLexerInfo import ExpressionLexerInfo
    from ..Types.TypeLexerInfo import TypeLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParameterLexerData(LexerData):
    Type: TypeLexerInfo
    Name: str
    Default: Optional[ExpressionLexerInfo]
    IsVarArgs: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.IsVarArgs is None or self.IsVarArgs, self
        super(ParameterLexerData, self).__post_init__()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParameterLexerRegions(LexerRegions):
    Type: Region
    Name: Region
    Default: Optional[Region]
    IsVarArgs: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParameterLexerInfo(LexerInfo):
    Data: ParameterLexerData
    Regions: ParameterLexerRegions


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParametersLexerData(LexerData):
    Positional: Optional[List[ParameterLexerInfo]]
    Keyword: Optional[List[ParameterLexerInfo]]
    Any: Optional[List[ParameterLexerInfo]]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParametersLexerRegions(LexerRegions):
    Positional: Optional[Region]
    Keyword: Optional[Region]
    Any: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParametersLexerInfo(LexerInfo):
    Data: ParametersLexerData
    Regions: ParametersLexerRegions
