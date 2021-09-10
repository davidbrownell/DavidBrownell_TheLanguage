# ----------------------------------------------------------------------
# |
# |  TupleNameLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-08 14:42:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleNameLexerInfo object"""

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
    from .NameLexerInfo import NameLexerData, NameLexerInfo
    from ...LexerInfo import LexerRegions, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleNameLexerData(NameLexerData):
    Names: List[NameLexerInfo]

    # TODO (Validation): Check for unique names


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleNameLexerRegions(LexerRegions):
    Names: Region
