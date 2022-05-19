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
        InvalidExpressionError,
        ParserInfo,
        ParserInfoType,
        TranslationUnitRegion,
    )

    from .FuncOrTypeExpressionParserInfo import (
        InvalidCompileTimeMutabilityModifierError,
        InvalidStandardMutabilityModifierError,
        MutabilityModifierRequiredError,
    )

    from ..Common.MutabilityModifier import MutabilityModifier

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
InvalidCompileTimeMutabilityError           = CreateError(
    "Compile-time types may not have a mutability modifier",
)


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
            **kwargs,
            regionless_attributes=["types", ],
        )

        # TODO: flatten

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsType() -> Optional[bool]:
        return True

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsType(
        self,
        parser_info_type: ParserInfoType,
        *,
        is_instantiated_type: Optional[bool]=True,
    ) -> None:
        errors: List[Error] = []

        for the_type in self.types:
            try:
                the_type.ValidateAsType(
                    parser_info_type,
                    is_instantiated_type=False,
                )
            except ErrorException as ex:
                errors += ex.errors

        if ParserInfoType.IsCompileTime(parser_info_type):
            if self.mutability_modifier is not None:
                errors.append(
                    InvalidCompileTimeMutabilityModifierError.Create(
                        region=self.regions__.mutability_modifier,
                    ),
                )

        elif (
            parser_info_type == ParserInfoType.Standard
            or parser_info_type == ParserInfoType.Unknown
        ):
            if is_instantiated_type and self.mutability_modifier is None:
                errors.append(
                    MutabilityModifierRequiredError.Create(
                        region=self.regions__.self__,
                    ),
                )
            elif not is_instantiated_type and self.mutability_modifier is not None:
                errors.append(
                    InvalidStandardMutabilityModifierError.Create(
                        region=self.regions__.mutability_modifier,
                    ),
                )

        else:
            assert False, parser_info_type  # pragma: no cover

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsExpression(self) -> None:
        raise ErrorException(
            InvalidExpressionError.Create(
                region=self.regions__.type__,
            ),
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "types", self.types  # type: ignore
