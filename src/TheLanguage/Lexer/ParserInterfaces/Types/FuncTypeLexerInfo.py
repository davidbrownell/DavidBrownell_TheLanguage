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

from typing import Any, List, Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...LexerInfo import (
        LexerData,
        LexerRegions,
        Region,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncTypeLexerData(LexerData):
    ReturnType: Any # TODO: TypeLexerInfo
    Parameters: Optional[List[Any]] # TODO: ExprLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncTypeLexerRegions(LexerRegions):
    ReturnType: Region
    Parameters: Optional[Region]
