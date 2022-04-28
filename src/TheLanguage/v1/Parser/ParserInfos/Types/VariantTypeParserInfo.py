# ----------------------------------------------------------------------
# |
# |  VariantTypeParserInfo.py
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
"""Contains the VariantTypeParserInfo object"""

import os

from typing import Generator, List

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeParserInfo import (           # pylint: disable=unused-import
        ParserInfoType,                     # convenience import
        TypeParserInfo,
    )

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
UnsupportedMutabilityModifierError          = CreateError(
    "Variant types must not have mutability modifiers",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariantTypeParserInfo(TypeParserInfo):
    # ----------------------------------------------------------------------
    types: List[TypeParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(VariantTypeParserInfo, self).__post_init__(*args, **kwargs)

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

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _EnumTypes(self) -> Generator[TypeParserInfo, None, None]:
        for the_type in self.types:
            if isinstance(the_type, VariantTypeParserInfo):
                yield from the_type._EnumTypes()  # pylint: disable=protected-access
            else:
                yield the_type
