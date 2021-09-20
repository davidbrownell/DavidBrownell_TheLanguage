# ----------------------------------------------------------------------
# |
# |  ParametersParserInfo.py
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
    from ..ParserInfo import ParserInfo
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ..Types.TypeParserInfo import TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParameterParserInfo(ParserInfo):
    Type: TypeParserInfo
    Name: str
    Default: Optional[ExpressionParserInfo]
    IsVarArgs: Optional[bool]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(ParameterParserInfo, self).__post_init__(regions)
        assert self.IsVarArgs is None or self.IsVarArgs, self


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParametersParserInfo(ParserInfo):
    Positional: Optional[List[ParameterParserInfo]]
    Keyword: Optional[List[ParameterParserInfo]]
    Any: Optional[List[ParameterParserInfo]]
