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
    from .TypeLexerInfo import TypeLexerInfo, Region
    from ..Common.TypeModifier import TypeModifier
    from ..LexerError import LexerError


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
class StandardTypeLexerInfo(TypeLexerInfo):
    TypeName: str
    Modifier: Optional[TypeModifier]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(StandardTypeLexerInfo, self).__post_init__(regions)

        invalid_modifiers = [
            TypeModifier.mutable,
            TypeModifier.immutable,
            TypeModifier.isolated,
            TypeModifier.shared,
            TypeModifier.ref,
        ]

        if self.Modifier in invalid_modifiers:
            assert self.Modifier is not None
            assert self.Regions.Modifier is not None  # type: ignore && pylint: disable=no-member

            valid_modifiers = [m for m in TypeModifier if m not in invalid_modifiers]

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

        assert self.Regions.Modifier is not None  # type: ignore && pylint: disable=no-member
        return self.Modifier, self.Regions.Modifier  # type: ignore && pylint: disable=no-member
