# ----------------------------------------------------------------------
# |
# |  TypePhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 08:28:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypePhrase object"""

import os

from typing import Any, Callable, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Error import CreateError, Error, ErrorException
    from ..Phrase import Phrase, Region

    from ..Common.MutabilityModifier import MutabilityModifier


# ----------------------------------------------------------------------
MutabilityModifierRequiredError             = CreateError(
    "A mutability modifier is required",
)

MutabilityModifierNotAllowedError           = CreateError(
    "A mutability modifier is not allowed in this context",
)

InvalidMutabilityModifierError              = CreateError(
    "'{modifier_str}' is not a valid mutability modifier in this context; valid modifiers are {valid_modifiers_str}",
    modifier=MutabilityModifier,
    valid_modifiers=List[MutabilityModifier],
    modifier_str=str,
    valid_modifiers_str=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypePhrase(Phrase):
    """Abstract base class for all types"""

    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    mutability_modifier: Optional[MutabilityModifier]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        regions,
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        super(TypePhrase, self).__init__(regions, regionless_attributes, validate, **custom_display_funcs)

        # Validate
        errors: List[Error] = []

        valid_modifiers = [
            MutabilityModifier.var,
            MutabilityModifier.ref,
            MutabilityModifier.val,
        ]

        if self.mutability_modifier is not None and self.mutability_modifier not in valid_modifiers:
            errors.append(
                InvalidMutabilityModifierError.Create(
                    region=self.regions__.mutability_modifier,
                    modifier=self.mutability_modifier,
                    valid_modifiers=valid_modifiers,
                    modifier_str=self.mutability_modifier.name,
                    valid_modifiers_str=", ".join("'{}'".format(v.name) for v in valid_modifiers),  # pylint: disable=no-member
                ),
            )

        if errors:
            raise ErrorException(*errors)
