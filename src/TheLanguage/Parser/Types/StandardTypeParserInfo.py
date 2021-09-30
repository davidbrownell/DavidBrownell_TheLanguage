# ----------------------------------------------------------------------
# |
# |  StandardTypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 10:45:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardTypeParserInfo object"""

import os

from typing import cast, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeParserInfo import Region, TypeModifier, TypeParserInfo
    from ..Error import Error


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidModifierError(Error):
    Modifier: str
    ValidModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' cannot be applied to standard types in this context; supported values are {ValidModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeParserInfo(TypeParserInfo):
    TypeName: str
    Modifier: Optional[TypeModifier]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(StandardTypeParserInfo, self).__post_init__(regions)

        # Not all modifiers are valid in this context
        valid_modifiers = [
            TypeModifier.var,
            TypeModifier.val,
            TypeModifier.view,
        ]

        if self.Modifier is not None and self.Modifier not in valid_modifiers:
            raise InvalidModifierError(
                self.Regions.Modifier,  # type: ignore && pylint: disable=no-member
                cast(str, self.Modifier.name),
                ", ".join(["'{}'".format(m.name) for m in valid_modifiers]),
            )

    # ----------------------------------------------------------------------
    @Interface.override
    def GetTypeModifier(self) -> Optional[Tuple[TypeModifier, Region]]:
        if self.Modifier is None:
            return None

        return (self.Modifier, self.Regions.Modifier)  # type: ignore && pylint: disable=no-member
