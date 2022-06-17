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

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import (
        ParserInfoType,
        ScopeFlag,
        StatementParserInfo,
        TranslationUnitRegion,
    )

    from .Traits.NamedStatementTrait import NamedStatementTrait

    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
class ImportType(Enum):
    source_is_module                        = auto()
    source_is_directory                     = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementParserInfo(
    NamedStatementTrait,
    StatementParserInfo,
):
    # ----------------------------------------------------------------------
    # |
    # |  Public Data
    # |
    # ----------------------------------------------------------------------
    source_parts: List[str]
    importing_name: str
    import_type: ImportType

    # ----------------------------------------------------------------------
    # |
    # |  Public Members
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        *args,
        **kwargs,
    ):
        return cls(
            ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
            ParserInfoType.Configuration,   # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, parser_info_type, regions, visibility_param):
        StatementParserInfo.__post_init__(
            self,
            parser_info_type,
            regions,
            regionless_attributes=[
                "import_type",
            ]
                + NamedStatementTrait.RegionlessAttributesArgs()
            ,
            validate=False,
            **NamedStatementTrait.ObjectReprImplBaseInitKwargs(),
        )

        # Set defaults
        if visibility_param is None:
            visibility_param = VisibilityModifier.private
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        NamedStatementTrait.__post_init__(self, visibility_param)

        # Validate
        self.ValidateRegions()

        errors: List[Error] = []

        if self.visibility == VisibilityModifier.protected:
            errors.append(
                InvalidProtectedError.Create(
                    region=self.regions__.visibility,
                ),
            )

        if errors:
            raise ErrorException(*errors)
