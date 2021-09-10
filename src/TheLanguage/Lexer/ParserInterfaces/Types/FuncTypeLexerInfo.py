# ----------------------------------------------------------------------
# |
# |  FuncTypeLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-08 17:05:37
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FuncTypeLexerInfo object"""

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
    from .TypeLexerInfo import TypeLexerData, TypeLexerInfo
    from ...LexerInfo import LexerRegions, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncTypeLexerData(TypeLexerData):
    ReturnType: TypeLexerInfo
    Parameters: Optional[List[TypeLexerInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Parameters is None or self.Parameters

        super(FuncTypeLexerData, self).__post_init__()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncTypeLexerRegions(LexerRegions):
    ReturnType: Region
    Parameters: Optional[Region]
