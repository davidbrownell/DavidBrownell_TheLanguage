# ----------------------------------------------------------------------
# |
# |  ImportStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 12:03:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ImportStatementParserInfo and ImportStatementItemParserInfo objects"""

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
    from .StatementParserInfo import ParserInfo, ParserInfoType, Region, StatementParserInfo

    from ..Common.VisibilityModifier import VisibilityModifier


# ----------------------------------------------------------------------
class ImportType(Enum):
    source_is_module                        = auto()
    source_is_directory                     = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementItemParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    name: str
    alias: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(ImportStatementItemParserInfo, self).__init__(ParserInfoType.Standard, *args, **kwargs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementParserInfo(StatementParserInfo):
    # ----------------------------------------------------------------------
    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    source_filename: str
    import_items: List[ImportStatementItemParserInfo]

    import_type: ImportType

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.Standard,        # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        super(ImportStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "import_items",
                "import_type",
            ],
            validate=False,
        )

        # Set defaults
        if visibility_param is None:
            visibility_param = VisibilityModifier.private
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        # Validate
        self.ValidateRegions()

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("ImportItems", self.import_items),
            ],  # type: ignore
            children=None,
        )
