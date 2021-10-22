# ----------------------------------------------------------------------
# |
# |  CastExpressionParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-04 09:03:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CastExpressionParserInfo object and errors generated during its use"""

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
    from .ExpressionParserInfo import ExpressionParserInfo

    from ..Common.TypeModifier import TypeModifier
    from ..Common.VisitorTools import StackHelper, VisitType

    from ..Types.TypeParserInfo import TypeParserInfo

    from ..Error import Error


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class TypeWithModifierError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Cast expressions may specify a type or a modifier, but not both.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidModifierError(Error):
    Modifier: str
    ValidModifiers: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "'{Modifier}' cannot be used in cast expressions; supported values are {ValidModifiers}.",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CastExpressionParserInfo(ExpressionParserInfo):
    Expression: ExpressionParserInfo
    Type: Union[TypeParserInfo, TypeModifier]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(CastExpressionParserInfo, self).__post_init__(regions)

        if isinstance(self.Type, TypeParserInfo):
            type_modifier_info = self.Type.GetTypeModifier()
            if type_modifier_info is not None:
                raise TypeWithModifierError(type_modifier_info[1])

        elif isinstance(self.Type, TypeModifier):
            valid_modifiers = [
                TypeModifier.ref,
                TypeModifier.val,
                TypeModifier.view,
            ]

            if self.Type not in valid_modifiers:
                raise InvalidModifierError(
                    self.Regions__.Type,  # type: ignore && pylint: disable=no-member
                    cast(str, self.Type.name),
                    ", ".join(["'{}'".format(e.name) for e in valid_modifiers]),
                )

        else:
            assert False, self.Type  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnCastExpression(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[self] as helper:
            with helper["Expression"]:
                self.Expression.Accept(visitor, helper.stack, *args, **kwargs)

            if isinstance(self.Type, TypeParserInfo):
                with helper["Type"]:
                    self.Type.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnCastExpression(stack, VisitType.Exit, self, *args, **kwargs)
