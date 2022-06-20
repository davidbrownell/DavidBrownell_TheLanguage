# ----------------------------------------------------------------------
# |
# |  RootStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-20 07:25:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RootStatementParserInfo object"""

import os

from typing import Dict, Generator, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import (
        ParserInfo,
        ParserInfoType,
        ScopeFlag,
        StatementParserInfo,
        TranslationUnitRegion,
    )

    from .Traits.NewNamespaceScopedStatementTrait import NewNamespaceScopedStatementTrait

    from ..Common.VisibilityModifier import VisibilityModifier


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class RootStatementParserInfo(
    NewNamespaceScopedStatementTrait,
    StatementParserInfo,
):
    # ----------------------------------------------------------------------
    statements: Optional[List[StatementParserInfo]]
    documentation: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        name: str,
        *args,
        **kwargs,
    ):
        # Duplicate regions for items that we are generating automatically
        regions.insert(0, regions[0])       # name
        regions.insert(0, regions[0])       # visibility

        return cls(  # pylint: disable=too-many-function-args
            ParserInfoType.Standard,        # type: ignore
            regions,                        # type: ignore
            name,
            VisibilityModifier.public,      # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        parser_info_type,
        regions,
        visibility_param,
        *args,
        **kwargs,
    ):
        self._InitTraits(
            allow_duplicate_names=False,
            allow_name_to_be_duplicated=False,
            name_is_ordered=False,
        )

        NewNamespaceScopedStatementTrait.__post_init__(self, visibility_param)

        StatementParserInfo.__post_init__(
            self,
            parser_info_type,
            regions,
            regionless_attributes=NewNamespaceScopedStatementTrait.RegionlessAttributesArgs(),
            *args,
            **{
                **kwargs,
                **NewNamespaceScopedStatementTrait.ObjectReprImplBaseInitKwargs(),
            },
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.Standard: ScopeFlag.Root,
        }

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptChildren(self) -> Generator[ParserInfo, None, None]:
        if self.statements:
            yield from self.statements
