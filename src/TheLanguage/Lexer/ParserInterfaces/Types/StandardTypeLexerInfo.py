# ----------------------------------------------------------------------
# |
# |  StandardTypeLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-08 16:24:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardTypeLexerInfo object"""

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
    from .TypeLexerInfo import TypeLexerData, TypeLexerInfo
    from ..Common.TypeModifier import TypeModifier
    from ...LexerError import LexerError
    from ...LexerInfo import LexerRegions, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidModifierError(LexerError):
    Modifier: str
    ValidModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' cannot be applied to standard types in this context; supported values are {ValidModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeLexerData(TypeLexerData):
    TypeName: str
    Modifier: Optional[TypeModifier]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeLexerRegions(LexerRegions):
    TypeName: Region
    Modifier: Optional[Region]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeLexerInfo(TypeLexerInfo):
    Data: StandardTypeLexerData
    Regions: StandardTypeLexerRegions

    # ----------------------------------------------------------------------
    def __post_init__(self):
        invalid_modifiers = [
            TypeModifier.mutable,
            TypeModifier.immutable,
            TypeModifier.isolated,
            TypeModifier.shared,
            TypeModifier.ref,
        ]

        if self.Data.Modifier in invalid_modifiers:
            assert self.Data.Modifier is not None
            assert self.Regions.Modifier is not None

            valid_modifiers = [m for m in TypeModifier if m not in invalid_modifiers]

            raise InvalidModifierError(
                self.Regions.Modifier,
                cast(str, self.Data.Modifier.name),
                ", ".join(["'{}'".format(m.name) for m in valid_modifiers]),
            )

        super(StandardTypeLexerInfo, self).__post_init__()

    # ----------------------------------------------------------------------
    @Interface.override
    def GetTypeModifier(self) -> Optional[Tuple[TypeModifier, Region]]:
        if self.Data.Modifier is None:
            return None

        assert self.Regions.Modifier is not None
        return self.Data.Modifier, self.Regions.Modifier
