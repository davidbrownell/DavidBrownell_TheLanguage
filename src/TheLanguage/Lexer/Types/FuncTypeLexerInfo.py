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
    from .TypeLexerInfo import TypeLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncTypeLexerInfo(TypeLexerInfo):
    ReturnType: TypeLexerInfo
    Parameters: Optional[List[TypeLexerInfo]] # TODO: This isn't right, should be based on parameters type
