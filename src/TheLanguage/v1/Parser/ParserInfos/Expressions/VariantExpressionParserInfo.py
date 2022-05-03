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

from typing import Callable, List, Optional

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
        regions: List[Optional[Region]],
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
    @Interface.override
    def ValidateAsConfigurationType(self) -> None:
        self._ValidateImpl(
            lambda parser_info: parser_info.ValidateAsConfigurationType(),
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateAsCustomizationType(self) -> None:
        self._ValidateImpl(
            lambda parser_info: parser_info.ValidateAsCustomizationType(),
        )

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

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _ValidateImpl(
        self,
        validate_func: Callable[[ExpressionParserInfo], None],
    ) -> None:
        errors: List[Error] = []

        if self.mutability_modifier is not None:
            errors.append(
                InvalidCompileTimeMutabilityError.Create(
                    region=self.regions__.mutability_modifier,
                ),
            )

        for the_type in self.types:
            try:
                validate_func(the_type)
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)
