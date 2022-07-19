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
    documentation: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        name: str,
        statements: List[StatementParserInfo],
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
            statements,
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
        StatementParserInfo.__post_init__(
            self,
            parser_info_type,
            regions,
            *args,
            **{
                **kwargs,
                **NewNamespaceScopedStatementTrait.ObjectReprImplBaseInitKwargs(),
                **{
                    "finalize": False,
                    "regionless_attributes": NewNamespaceScopedStatementTrait.RegionlessAttributesArgs(),
                },
            },
        )

        self._InitTraits(
            allow_duplicate_names=False,
            allow_name_to_be_duplicated=False,
        )

        NewNamespaceScopedStatementTrait.__post_init__(self, visibility_param)

        self._Finalize()

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        return {
            ParserInfoType.Standard: ScopeFlag.Root,
        }

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(*args, **kwargs) -> bool:
        return True
