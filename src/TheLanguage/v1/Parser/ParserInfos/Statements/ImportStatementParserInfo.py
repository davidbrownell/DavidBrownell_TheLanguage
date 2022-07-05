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

from contextlib import contextmanager
from enum import auto, Enum
from typing import Dict, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

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

    from ..Common.VisibilityModifier import VisibilityModifier, InvalidProtectedError
    from ..Traits.NamedTrait import NamedTrait

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
class ImportType(Enum):
    source_is_module                        = auto()
    source_is_directory                     = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ImportStatementParserInfo(
    NamedTrait,
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
                + NamedTrait.RegionlessAttributesArgs()
            ,
            validate=False,
            **NamedTrait.ObjectReprImplBaseInitKwargs(),
        )

        # Set defaults
        if visibility_param is None:
            visibility_param = VisibilityModifier.private
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        NamedTrait.__post_init__(self, visibility_param)

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

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.Configuration: ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
        }

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(
        scope_flag: ScopeFlag,
    ) -> bool:
        return True

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(*args, **kwargs):  # pylint: disable=unused-argument
        # Nothing to do here
        yield
