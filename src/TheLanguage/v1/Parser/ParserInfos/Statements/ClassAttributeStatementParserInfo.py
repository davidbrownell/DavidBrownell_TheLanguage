# ----------------------------------------------------------------------
# |
# |  ClassAttributeStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 11:53:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassAttributeStatementParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfoType, Region, StatementParserInfo
    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.MutabilityModifier import MutabilityModifier
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ..Types.TypeParserInfo import (
        InvalidNewMutabilityModifierError,
        MutabilityModifierRequiredError,
        TypeParserInfo,
    )

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
InvalidAttributeError                       = CreateError(
    "'{type}' types do not support attributes of any kind",
    type=str,
)

InvalidVisibilityError                      = CreateError(
    "'{visibility_str}' is not a valid visibility for '{type}' attributes; valid visibilities are {valid_visibilities_str}",
    type=str,
    visibility=VisibilityModifier,
    valid_visibilities=List[VisibilityModifier],
    visibility_str=str,
    valid_visibilities_str=str,
)

InvalidMutabilityModifierError              = CreateError(
    "'{mutability_str}' is not a valid mutability modifier for '{type}' attributes; valid mutabilities are {valid_mutabilities_str}",
    type=str,
    mutability=MutabilityModifier,
    valid_mutabilities=List[MutabilityModifier],
    mutability_str=str,
    valid_mutabilities_str=str,
)

InvalidMutablePublicAttributeError          = CreateError(
    "'{type}' types do not support public mutable attributes",
    type=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ClassAttributeStatementParserInfo(StatementParserInfo):
    """Attribute of a class"""

    # ----------------------------------------------------------------------
    class_capabilities: ClassCapabilities

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    type: TypeParserInfo

    name: str
    documentation: Optional[str]

    initialized_value: Optional[ExpressionParserInfo]

    keyword_initialization: Optional[bool]
    no_initialization: Optional[bool]
    no_serialize: Optional[bool]
    no_compare: Optional[bool]
    is_override: Optional[bool]

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
        super(ClassAttributeStatementParserInfo, self).__post_init__(
            parser_info_type,
            regions,
            regionless_attributes=[
                "class_capabilities",
                "type",
                "initialized_value",
            ],
            validate=False,
            class_capabilities=lambda value: value.name,
        )

        # Set defaults
        if visibility_param is None and self.class_capabilities.default_attribute_visibility is not None:
            visibility_param = self.class_capabilities.default_attribute_visibility
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        self.ValidateRegions()

        # Validate
        errors: List[Error] = []

        if not self.class_capabilities.valid_attribute_visibilities:
            errors.append(
                InvalidAttributeError.Create(
                    region=self.regions__.self__,
                    type=self.class_capabilities.name,
                ),
            )

        else:
            if self.visibility not in self.class_capabilities.valid_attribute_visibilities:
                errors.append(
                    InvalidVisibilityError.Create(
                        region=self.regions__.visibility,
                        type=self.class_capabilities.name,
                        visibility=self.visibility,
                        valid_visibilities=self.class_capabilities.valid_attribute_visibilities,
                        visibility_str=self.visibility.name,
                        valid_visibilities_str=", ".join("'{}'".format(v.name) for v in self.class_capabilities.valid_attribute_visibilities),
                    ),
                )

        if self.type.mutability_modifier is None:
            errors.append(
                MutabilityModifierRequiredError.Create(
                    region=self.type.regions__.self__,
                ),
            )
        elif self.type.mutability_modifier == MutabilityModifier.new:
            errors.append(
                InvalidNewMutabilityModifierError.Create(
                    region=self.type.regions__.mutability_modifier,
                ),
            )
        else:
            if self.type.mutability_modifier not in self.class_capabilities.valid_attribute_mutabilities:
                errors.append(
                    InvalidMutabilityModifierError.Create(
                        region=self.type.regions__.mutability_modifier,
                        type=self.class_capabilities.name,
                        mutability=self.type.mutability_modifier,
                        valid_mutabilities=self.class_capabilities.valid_attribute_mutabilities,
                        mutability_str=self.type.mutability_modifier.name,
                        valid_mutabilities_str=", ".join("'{}'".format(m.name) for m in self.class_capabilities.valid_attribute_mutabilities),
                    ),
                )

            if (
                self.visibility == VisibilityModifier.public
                and self.type.mutability_modifier in [MutabilityModifier.var, MutabilityModifier.ref, MutabilityModifier.view]
                and not self.class_capabilities.allow_mutable_public_attributes
            ):
                errors.append(
                    InvalidMutablePublicAttributeError.Create(
                        region=self.regions__.self__,
                        type=self.class_capabilities.name,
                    ),
                )

        if errors:
            raise ErrorException(*errors)
