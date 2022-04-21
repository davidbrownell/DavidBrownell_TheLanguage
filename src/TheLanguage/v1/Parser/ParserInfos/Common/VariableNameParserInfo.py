# ----------------------------------------------------------------------
# |
# |  VariableNameParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 16:50:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableNameParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, ParserInfoType, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableNameParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[Region]]]

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
        super(VariableNameParserInfo, self).__init__(*args, **kwargs)
