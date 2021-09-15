# ----------------------------------------------------------------------
# |
# |  CastExpressionLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-10 14:32:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CastExpressionLexerData, CastExpressionLexerRegions, and CastExpressionLexerInfo objects"""

import os

from typing import cast, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ExpressionLexerInfo import ExpressionLexerInfo

    from ..Common.TypeModifier import TypeModifier
    from ..Types.TypeLexerInfo import TypeLexerInfo

    from ..LexerError import LexerError


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeWithModifierError(LexerError):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Cast expressions may specify a type or a modifier, but not both.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidModifierError(LexerError):
    Modifier: str
    ValidModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' cannot be used with cast expressions; supported values are {ValidModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CastExpressionLexerInfo(ExpressionLexerInfo):
    Expression: ExpressionLexerInfo
    Type: Union[TypeLexerInfo, TypeModifier]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(CastExpressionLexerInfo, self).__post_init__(regions)

        if isinstance(self.Type, TypeLexerInfo):
            type_modifier_info = self.Type.GetTypeModifier()
            if type_modifier_info is not None:
                raise TypeWithModifierError(type_modifier_info[1])

        elif isinstance(self.Type, TypeModifier):
            valid_modifiers = [TypeModifier.ref, TypeModifier.val, TypeModifier.view]

            if self.Type not in valid_modifiers:
                raise InvalidModifierError(
                    self.Regions.Type,  # pylint: disable=no-member
                    cast(str, self.Type.name),
                    ", ".join(["'{}'".format(m.name) for m in valid_modifiers]),
                )
        else:
            assert False, self.Type  # pragma: no cover
