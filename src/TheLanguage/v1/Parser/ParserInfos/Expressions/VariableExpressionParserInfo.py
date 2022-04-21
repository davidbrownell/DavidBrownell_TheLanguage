# ----------------------------------------------------------------------
# |
# |  VariableExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-20 15:06:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableExpressionParserInfo object"""

import os

from typing import Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

    is_compile_time_param: InitVar[bool]
    is_compile_time: Optional[bool]         = field(init=False)

    name: str

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, is_compile_time_param):  # type: ignore
        if is_compile_time_param:
            parser_info_type = ParserInfoType.CompileTime
        else:
            parser_info_type = ParserInfoType.Standard
            is_compile_time_param = None

        object.__setattr__(self, "is_compile_time", is_compile_time_param)

        super(VariableExpressionParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=["name", ],
        )
