# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-26 17:01:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains variant-related types"""

import os

from typing import List

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GenericType import GenericType

    from ...Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ...Types.ConcreteType import ConcreteType
    from ...Types.ConstrainedType import ConstrainedType

    from ....Error import Error, ErrorException


# ----------------------------------------------------------------------
class GenericVariantType(GenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: VariantExpressionParserInfo,
        generic_types: List[GenericType],
    ):
        super(GenericVariantType, self).__init__(parser_info)

        self.generic_types                  = generic_types

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> VariantExpressionParserInfo:
        assert isinstance(self._parser_info, VariantExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSameType(
        self,
        other: GenericType,
    ) -> bool:
        return (
            isinstance(other, GenericVariantType)
            and len(self.generic_types) == len(other.generic_types)
            and all(
                this_type.IsSameType(that_type)
                for this_type, that_type in zip(self.generic_types, other.generic_types)
            )
        )


# ----------------------------------------------------------------------
class ConcreteVariantType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: VariantExpressionParserInfo,
        concrete_types: List[ConcreteType],
    ):
        super(ConcreteVariantType, self).__init__(parser_info)

        self.concrete_types                 = concrete_types

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> VariantExpressionParserInfo:
        assert isinstance(self._parser_info, VariantExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        errors: List[Error] = []

        for concrete_type in self.concrete_types:
            try:
                concrete_type.FinalizePass1()
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        errors: List[Error] = []

        for concrete_type in self.concrete_types:
            try:
                concrete_type.FinalizePass2()
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(
        self,
    ) -> "ConstrainedVariantType":
        constrained_types: List[ConstrainedType] = []
        errors: List[Error] = []

        for concrete_type in self.concrete_types:
            try:
                constrained_types.append(concrete_type.CreateConstrainedType())
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        return ConstrainedVariantType(self, constrained_types)


# ----------------------------------------------------------------------
class ConstrainedVariantType(ConstrainedType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        concrete_type: ConcreteVariantType,
        constrained_types: List[ConstrainedType],
    ):
        super(ConstrainedVariantType, self).__init__(concrete_type)

        self.constrained_types              = constrained_types
