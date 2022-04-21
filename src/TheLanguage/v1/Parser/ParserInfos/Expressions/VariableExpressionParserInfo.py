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

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    is_compile_time: Optional[bool]
    name: str

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        is_compile_time: bool,
        *args,
        **kwargs,
    ):
        if is_compile_time:
            parser_info_type = ParserInfoType.CompileTime
            is_compile_time_value = True
        else:
            parser_info_type = ParserInfoType.Standard
            is_compile_time_value = None

        return cls(
            parser_info_type,               # type: ignore
            regions,                        # type: ignore
            is_compile_time_value,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(VariableExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=["name", ],
        )
