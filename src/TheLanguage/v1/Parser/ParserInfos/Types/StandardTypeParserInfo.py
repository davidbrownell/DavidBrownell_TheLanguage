# ----------------------------------------------------------------------
# |
# |  StandardTypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 10:46:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardTypeParserInfo object"""

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
    from .TypeParserInfo import ParserInfo, ParserInfoType, Region, TypeParserInfo

    from ..Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ..Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeItemParserInfo(ParserInfo):
    parser_info_type__: ParserInfoType      = field(init=False)

    regions: InitVar[List[Optional[Region]]]

    name: str

    templates: Optional[TemplateArgumentsParserInfo]
    constraints: Optional[ConstraintArgumentsParserInfo]

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
        super(StandardTypeItemParserInfo, self).__init__(
            ParserInfoType.Unknown,
            regions,
            regionless_attributes=[
                "templates",
                "constraints",
            ],
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeParserInfo(TypeParserInfo):
    items: List[StandardTypeItemParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type__, regions):  # type: ignore
        super(StandardTypeParserInfo, self).__post_init__(parser_info_type__, regions)
