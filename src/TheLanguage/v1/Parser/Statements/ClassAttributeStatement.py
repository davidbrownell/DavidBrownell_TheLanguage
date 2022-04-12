# ----------------------------------------------------------------------
# |
# |  ClassAttributeStatement.py
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
"""Contains the ClassAttributeStatement object"""

import os

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
    from .ClassCapabilities.ClassCapabilities import ClassCapabilities

    from ..Common.ConcreteTypePhrase import ConcreteTypePhrase
    from ..Common.MutabilityModifier import MutabilityModifier
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Phrase import Phrase, Region

    from ...Common.Diagnostics import CreateError, DiagnosticsError, Error


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

InvalidMutabilityError                      = CreateError(
    "'{mutability_str}' is not a valid mutability for '{type}' attributes; valid mutabilities are {valid_mutabilities_str}",
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
class ClassAttributeStatement(Phrase):
    """Attribute of a class"""

    class_capabilities: InitVar[ClassCapabilities]
    regions: InitVar[List[Optional[Region]]]

    visibility_param: InitVar[Optional[VisibilityModifier]]
    visibility: VisibilityModifier          = field(init=False)

    type: ConcreteTypePhrase
    mutability: MutabilityModifier

    name: str
    documentation: Optional[str]

    initialized_value: Optional[Phrase]

    keyword_initialization: Optional[bool]
    no_initialization: Optional[bool]
    no_serialize: Optional[bool]
    no_compare: Optional[bool]
    is_override: Optional[bool]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, class_capabilities, regions, visibility_param):
        super(ClassAttributeStatement, self).__init__(
            regions,
            validate=False,
        )

        # Set defaults
        if visibility_param is None:
            visibility_param = class_capabilities.default_attribute_visibility
            object.__setattr__(self.regions__, "visibility", self.regions__.self__)

        object.__setattr__(self, "visibility", visibility_param)

        self.ValidateRegions()

        # Validate
        errors: List[Error] = []

        if not class_capabilities.valid_attribute_visibilities:
            errors.append(
                InvalidAttributeError.Create(
                    region=self.regions__.self__,
                    type=class_capabilities.name,
                ),
            )

        else:
            if self.visibility not in class_capabilities.valid_attribute_visibilities:
                errors.append(
                    InvalidVisibilityError.Create(
                        region=self.regions__.visibility,
                        type=class_capabilities.name,
                        visibility=self.visibility,
                        valid_visibilities=class_capabilities.valid_attribute_visibilities,
                        visibility_str=self.visibility.name,
                        valid_visibilities_str=", ".join("'{}'".format(v.name) for v in class_capabilities.valid_attribute_visibilities),
                    ),
                )

            if self.mutability not in class_capabilities.valid_attribute_mutabilities:
                errors.append(
                    InvalidMutabilityError.Create(
                        region=self.regions__.mutability,
                        type=class_capabilities.name,
                        mutability=self.mutability,
                        valid_mutabilities=class_capabilities.valid_attribute_mutabilities,
                        mutability_str=self.mutability.name,
                        valid_mutabilities_str=", ".join("'{}'".format(m.name) for m in class_capabilities.valid_attribute_mutabilities),
                    ),
                )

            if (
                self.visibility == VisibilityModifier.public
                and self.mutability & MutabilityModifier.mutable
                and not class_capabilities.allow_mutable_public_attributes
            ):
                errors.append(
                    InvalidMutablePublicAttributeError.Create(
                        region=self.regions__.self__,
                        type=class_capabilities.name,
                    ),
                )

        if errors:
            raise DiagnosticsError(
                errors=errors
            )
