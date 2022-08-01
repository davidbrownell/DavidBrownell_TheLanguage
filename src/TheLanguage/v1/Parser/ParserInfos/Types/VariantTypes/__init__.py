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
    from ..GenericTypes import BoundGenericType, GenericType

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
            all(generic_type.is_default_initializable for generic_type in generic_types),
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
    def CreateBoundGenericType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> BoundGenericType:
        assert parser_info is self.parser_info, (parser_info, self.parser_info)
        return VariantBoundGenericType(self)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> ConcreteType:
        return self.CreateBoundGenericType(self.parser_info).CreateConcreteType()


# ----------------------------------------------------------------------
class VariantBoundGenericType(BoundGenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        generic_type: VariantGenericType,
    ):
        super(VariantBoundGenericType, self).__init__(generic_type, generic_type.parser_info)

        self.bound_generic_types            = [
            generic_type.CreateBoundGenericType(parser_info)
            for generic_type, parser_info in zip(
                generic_type.generic_types,
                generic_type.parser_info.types
            )
        ]

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(self) -> ConcreteType:
        return ConcreteVariantType(
            self.generic_type.parser_info,
            [
                bound_generic_type.CreateConcreteType()
                for bound_generic_type in self.bound_generic_types
            ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def IsCovariant(
        self,
        other: GenericType,
    ) -> bool:
        if not isinstance(other, VariantBoundGenericType):
            return False

        if len(self.bound_generic_types) != len(other.bound_generic_types):
            return False

        return (
            all(
                this.IsCovariant(that)
                for this, that in zip(self.bound_generic_types, other.bound_generic_types)
            )
            and self.generic_type.parser_info.mutability_modifier == other.generic_type.parser_info.mutability_modifier
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
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass1))

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass2))

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass3Impl(self) -> None:
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass3))

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass4Impl(self) -> None:
        self._FinalizeImpl(lambda concrete_type: concrete_type.Finalize(ConcreteType.State.FinalizedPass4))

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
class ConstrainedVariantType(ConstrainedType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        concrete_type: ConcreteVariantType,
        constrained_types: List[ConstrainedType],
    ):
        super(ConstrainedVariantType, self).__init__(concrete_type)

        self.constrained_types              = constrained_types
