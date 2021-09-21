# ----------------------------------------------------------------------
# |
# |  ImportStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-20 12:43:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types that defined functionality used when important content"""

import os

from enum import auto, Enum
from typing import List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import StatementParserInfo, ParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier


# ----------------------------------------------------------------------
class ImportType(Enum):
    SourceIsModule                          = auto()
    SourceIsDirectory                       = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportItemParserInfo(ParserInfo):
    Name: str
    Alias: Optional[str]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementParserInfo(StatementParserInfo):
    visibility: InitVar[VisibilityModifier]
    Visibility: VisibilityModifier          = field(init=False)

    ImportType: ImportType
    SourceFilename: str
    ImportItems: List[ImportItemParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, visibility):
        super(ImportStatementParserInfo, self).__post_init__(
            regions,
            should_validate=False,
        )

        # Visibility
        if visibility is None:
            visibility = VisibilityModifier.private
            object.__setattr__(self.Regions, "Visibility", self.Regions.Self__)  # type: ignore && pylint: disable=no-member

        object.__setattr__(self, "Visibility", visibility)

        # Validate
        self.Validate()
