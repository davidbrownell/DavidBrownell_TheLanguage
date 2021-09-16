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
    from ..LexerInfo import LexerInfo
    from ..Expressions.ExpressionLexerInfo import ExpressionLexerInfo
    from ..Types.TypeLexerInfo import TypeLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParameterLexerInfo(LexerInfo):
    Type: TypeLexerInfo
    Name: str
    Default: Optional[ExpressionLexerInfo]
    IsVarArgs: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(ParameterLexerInfo, self).__post_init__(regions)
        assert self.IsVarArgs is None or self.IsVarArgs, self


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParametersLexerInfo(LexerInfo):
    Positional: Optional[List[ParameterLexerInfo]]
    Keyword: Optional[List[ParameterLexerInfo]]
    Any: Optional[List[ParameterLexerInfo]]
