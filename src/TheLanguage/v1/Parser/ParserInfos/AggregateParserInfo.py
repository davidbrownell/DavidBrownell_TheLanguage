# ----------------------------------------------------------------------
# |
# |  AggregateParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-20 10:57:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the AggregateParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ParserInfo import ParserInfo, ParserInfoType
    from ..TranslationUnitRegion import Location, TranslationUnitRegion


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class AggregateParserInfo(ParserInfo):
    """Contains multiple ParserInfo objects while maintaining an interface as if it was one"""

    # ----------------------------------------------------------------------
    parser_infos: List[ParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        min_location: Optional[Location] = None
        max_location: Optional[Location] = None

        for parser_info in self.parser_infos:
            if min_location is None or parser_info.regions__.self__.begin < min_location:
                min_location = parser_info.regions__.self__.begin
            if max_location is None or parser_info.regions__.self__.end > max_location:
                max_location = parser_info.regions__.self__.end

        assert min_location is not None
        assert max_location is not None

        super(AggregateParserInfo, self).__init__(
            ParserInfoType.Unknown,
            regions=[
                TranslationUnitRegion.Create(
                    min_location,
                    max_location,
                ),
            ],
            regionless_attributes=["parser_infos", ],
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:
        yield "parser_infos", self.parser_infos  # type: ignore
