# ----------------------------------------------------------------------
# |
# |  ImportStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-15 14:11:08
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types that define functionality used when importing content"""

import os

from enum import auto, Enum
from typing import List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfo, StatementParserInfo
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..Common.VisitorTools import StackHelper


# ----------------------------------------------------------------------
class ImportType(Enum):
    SourceIsModule                          = auto()
    SourceIsDirectory                       = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementItemParserInfo(ParserInfo):
    Name: str
    Alias: Optional[str]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementParserInfo(StatementParserInfo):
    visibility: InitVar[Optional[VisibilityModifier]]

    Visibility: VisibilityModifier          = field(init=False)
    SourceFilename: str
    ImportItems: List[ImportStatementItemParserInfo]
    ImportType: ImportType

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, visibility):
        super(ImportStatementParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["ImportItems", "ImportType"],
            should_validate=False,
        )

        # Visibility
        if visibility is None:
            visibility = VisibilityModifier.private
            object.__setattr__(self.Regions__, "Visibility", self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

        object.__setattr__(self, "Visibility", visibility)

        self.Validate()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[(self, "ImportItems")] as helper:
            for import_item in self.ImportItems:
                import_item.Accept(visitor, helper.stack, *args, **kwargs)
