# ----------------------------------------------------------------------
# |
# |  VariantType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 09:02:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantType object"""

import os

from typing import Generator, List, Set

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypePhrase import (
        CreateError,
        DiagnosticsError,
        Error,
        TypePhrase
    )


# ----------------------------------------------------------------------
UnsupportedMutabilityModifierError          = CreateError(
    "Variant types must not have mutability modifiers",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariantType(TypePhrase):
    types: List[TypePhrase]
    flattened_types: List[TypePhrase]       = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(VariantType, self).__post_init__(
            regions,
            regionless_attributes=["flattened_types"],
        )

        # Validate
        errors: List[Error] = []

        for contained_type in self.types:
            if contained_type.mutability_modifier is not None:
                errors.append(
                    UnsupportedMutabilityModifierError.Create(
                        region=contained_type.regions__.mutability_modifier,
                    ),
                )

        if errors:
            raise DiagnosticsError(
                errors=errors,
            )

        # Flatten the types
        flattened_types: List[TypePhrase] = []
        flattened_types_lookup: Set[TypePhrase] = set()

        # TODO: for the_type in self._EnumTypes():
        # TODO:     if the_type not in flattened_types_lookup:
        # TODO:         flattened_types.append(the_type)
        # TODO:         flattened_types_lookup.add(the_type)

        object.__setattr__(self, "flattened_types", flattened_types)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _EnumTypes(self) -> Generator[TypePhrase, None, None]:
        for the_type in self.types:
            if isinstance(the_type, VariantType):
                yield from the_type._EnumTypes()  # pylint: disable=protected-access
            else:
                yield the_type
