# ----------------------------------------------------------------------
# |
# |  VariantExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-01 14:05:36
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantExpressionParserInfo object"""

import os

from contextlib import contextmanager
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
    from .ExpressionParserInfo import (
        ExpressionParserInfo,
        ParserInfo,
        ParserInfoType,
        TranslationUnitRegion,
    )

    from ..Common.MutabilityModifier import MutabilityModifier

    from ...Error import Error, ErrorException


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariantExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    types: List[ExpressionParserInfo]
    mutability_modifier: Optional[MutabilityModifier]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        types: List[ExpressionParserInfo],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.GetDominantType(*types),     # type: ignore
            regions,                                    # type: ignore
            types,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(VariantExpressionParserInfo, self).__post_init__(
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": ["types", ],
                },
            },
        )

        # TODO: flatten

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsType() -> Optional[bool]:
        return True

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "types", self.types  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def _InitializeAsTypeImpl(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: bool=True,
    ) -> None:
        errors: List[Error] = []

        try:
            MutabilityModifier.Validate(self, parser_info_type, is_instantiated_type)
        except ErrorException as ex:
            errors += ex.errors

        for the_type in self.types:
            try:
                the_type.InitializeAsType(
                    parser_info_type,
                    is_instantiated_type=False,
                )
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    @Interface.override
    def _InitConfigurationImpl(*args, **kwargs):  # pylint: disable=unused-argument
        # Nothing to do here
        yield
