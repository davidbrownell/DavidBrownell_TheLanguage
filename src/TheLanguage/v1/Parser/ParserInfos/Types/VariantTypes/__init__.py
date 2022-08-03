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

from typing import Callable, List

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GenericType import GenericType

    from ...Expressions.VariantExpressionParserInfo import ExpressionParserInfo, VariantExpressionParserInfo

    from ...Types.ConcreteType import ConcreteType
    from ...Types.ConstrainedType import ConstrainedType

    from ....Error import Error, ErrorException


# ----------------------------------------------------------------------
class VariantGenericType(GenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: VariantExpressionParserInfo,
        generic_types: List[GenericType],
    ):
        super(VariantGenericType, self).__init__(
            parser_info,
            is_default_initializable=all(generic_type.is_default_initializable for generic_type in generic_types),
        )

        self.generic_types                  = generic_types

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> VariantExpressionParserInfo:
        assert isinstance(self._parser_info, VariantExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        expression_parser_info: ExpressionParserInfo,
    ) -> ConcreteType:
        assert expression_parser_info is self.parser_info, (expression_parser_info, self.parser_info)
        return self._CreateDefaultConcreteTypeImpl()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> ConcreteType:
        concrete_types: List[ConcreteType] = []
        errors: List[Error] = []

        for generic_type, generic_parser_info in zip(
            self.generic_types,
            self.parser_info.types,
        ):
            try:
                concrete_types.append(generic_type.CreateConcreteType(generic_parser_info))
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        return VariantConcreteType(self.parser_info, concrete_types)


# ----------------------------------------------------------------------
class VariantConcreteType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: VariantExpressionParserInfo,
        concrete_types: List[ConcreteType],
    ):
        super(VariantConcreteType, self).__init__(
            parser_info,
            is_default_initializable=all(
                concrete_type.is_default_initializable for concrete_type in concrete_types
            ),
        )

        self.concrete_types                 = concrete_types

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> VariantExpressionParserInfo:
        assert isinstance(self._parser_info, VariantExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def IsMatch(
        self,
        other: ConcreteType,
    ) -> bool:
        return (
            isinstance(other, VariantConcreteType)
            and len(self.concrete_types) == len(other.concrete_types)
            and all(this.IsMatch(that) for this, that in zip(self.concrete_types, other.concrete_types))
            and self.parser_info.mutability_modifier == other.parser_info.mutability_modifier
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsCovariant(
        self,
        other: ConcreteType,
    ) -> bool:
        return (
            isinstance(other, VariantConcreteType)
            and len(self.concrete_types) == len(other.concrete_types)
            and all(this.IsCovariant(that) for this, that in zip(self.concrete_types, other.concrete_types))
            and self.parser_info.mutability_modifier == other.parser_info.mutability_modifier
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass1))

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass2))

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(
        self,
        expression_parser_info: ExpressionParserInfo,
    ) -> ConstrainedType:
        assert expression_parser_info is self.parser_info, (expression_parser_info, self.parser_info)
        return self._CreateDefaultConstrainedTypeImpl()

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConstrainedTypeImpl(self) -> ConstrainedType:
        return VariantConstrainedType(self, self.concrete_types)

    # ----------------------------------------------------------------------
    def _FinalizeImpl(
        self,
        finalize_func: Callable[[ConcreteType], None],
    ) -> None:
        errors: List[Error] = []

        for concrete_type in self.concrete_types:
            try:
                finalize_func(concrete_type)
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)


# ----------------------------------------------------------------------
class VariantConstrainedType(ConstrainedType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        concrete_type: VariantConcreteType,
        concrete_types: List[ConcreteType],
    ):
        super(VariantConstrainedType, self).__init__(concrete_type, concrete_type.parser_info.mutability_modifier)

        constrained_types: List[ConstrainedType] = []
        errors: List[Error] = []

        for child_concrete_type, type_parser_info in zip(
            concrete_types,
            concrete_type.parser_info.types,
        ):
            try:
                constrained_types.append(child_concrete_type.CreateConstrainedType(type_parser_info))
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        self.constrained_types              = constrained_types
