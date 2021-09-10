# ----------------------------------------------------------------------
# |
# |  VariantTypeLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-08 16:52:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantTypeLexerInfo object"""

import os

from typing import List

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...LexerInfo import LexerData, LexerRegions, LexerInfo, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariantTypeLexerData(LexerData):
    Types: List[LexerInfo]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariantTypeLexerRegions(LexerRegions):
    Types: Region
