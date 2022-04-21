# ----------------------------------------------------------------------
# |
# |  StringExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 12:00:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StringExpressionParserInfo object"""

import os

from dataclasses import dataclass, field

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
class StringExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type__: ParserInfoType      = field(init=False)

    value: str

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):  # type: ignore
        super(StringExpressionParserInfo, self).__post_init__(
            ParserInfoType.Unknown,
            regions,
            regionless_attributes=["value", ],
        )
