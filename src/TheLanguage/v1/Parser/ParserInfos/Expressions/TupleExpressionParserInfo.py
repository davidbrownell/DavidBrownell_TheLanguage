# ----------------------------------------------------------------------
# |
# |  TupleExpressionParserInfo.py
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
"""Contains the TupleExpressionParserInfo object"""

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
    from .ExpressionParserInfo import ExpressionParserInfo, ParserInfoType, Region
    from .FuncOrTypeExpressionParserInfo import (
        MutabilityModifierRequiredError,
        InvalidStandardMutabilityModifierError,
    )

    from ..Common.MutabilityModifier import MutabilityModifier

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
CompileTimeTupleError                       = CreateError(
    "Tuples are not supported at compile-time",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleExpressionParserInfo(ExpressionParserInfo):
    # ----------------------------------------------------------------------
    types: List[ExpressionParserInfo]
    mutability_modifier: Optional[MutabilityModifier]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        types: List[ExpressionParserInfo],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.GetDominantType(*types),     # type: ignore
            regions,                                    # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(TupleExpressionParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=["types", ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsType(self) -> Optional[bool]:
        for the_type in self.types:
            result = the_type.IsType()

            if result is False:
                return False

        return True

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsType(
        self,
        parser_info_type: ParserInfoType,               # pylint: disable=unused-argument
        *,
        is_instantiated_type: Optional[bool]=True,      # pylint: disable=unused-argument
    ):
        errors: List[Error] = []

        if (
            parser_info_type == ParserInfoType.Configuration
            or parser_info_type == ParserInfoType.TypeCustomization
        ):
            errors.append(
                CompileTimeTupleError.Create(
                    region=self.regions__.self__,
                ),
            )

        elif (
            parser_info_type == ParserInfoType.Standard
            or parser_info_type == ParserInfoType.Unknown
        ):
            for the_type in self.types:
                try:
                    the_type.ValidateAsType(
                        parser_info_type,
                        is_instantiated_type=True,
                    )
                except ErrorException as ex:
                    errors += ex.errors

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
        errors: List[Error] = []

        for the_type in self.types:
            try:
                the_type.ValidateAsExpression()
            except ErrorException as ex:
                errors += ex.errors

        if self.mutability_modifier is not None:
            errors.append(
                InvalidStandardMutabilityModifierError.Create(
                    region=self.regions__.mutability_modifier,
                ),
            )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("types", self.types),
            ],  # type: ignore
            children=None,
        )
