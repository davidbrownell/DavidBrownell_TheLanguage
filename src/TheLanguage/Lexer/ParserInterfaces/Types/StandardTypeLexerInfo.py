# ----------------------------------------------------------------------
# |
# |  StandardTypeLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-08 16:24:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardTypeLexerInfo object"""

import os

from typing import Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.TypeModifier import TypeModifier
    from ...LexerInfo import LexerData, LexerRegions, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeLexerData(LexerData):
    TypeName: str
    Modifier: Optional[TypeModifier]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeLexerRegions(LexerRegions):
    TypeName: Region
    Modifier: Optional[Region]
