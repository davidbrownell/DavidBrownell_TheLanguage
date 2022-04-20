# ----------------------------------------------------------------------
# |
# |  CapturedVariablesParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-15 08:35:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CapturedVariablesParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo, ParserInfo, ParserInfoType, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CapturedVariablesParserInfo(ParserInfo):
    parser_info_type__: ParserInfoType      = field(init=False)

    regions: InitVar[List[Optional[Region]]]
    variables: List[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(CapturedVariablesParserInfo, self).__init__(ParserInfoType.Standard, regions)

        # TODO: Validate that all variables are ultimately variable expressions (dotted notation is OK)
        # TODO: Is dotted notation OK? Capturing variables is a bit like adding a ref; need to think about this more
