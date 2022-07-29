# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-26 17:00:13
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains tuple-related types"""

import os

from typing import List, Optional

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GenericTypes import GenericExpressionType, GenericType

    from ...Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo

    from ...Types.ConcreteType import ConcreteType
    from ...Types.ConstrainedType import ConstrainedType

    from ....Error import Error, ErrorException


# ----------------------------------------------------------------------
class GenericTupleType(GenericExpressionType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: TupleExpressionParserInfo,
        generic_types: List[GenericType],
    ):
        super(GenericTupleType, self).__init__(
            parser_info,
            all(generic_type.is_default_initializable for generic_type in generic_types),
        )

        self.generic_types                  = generic_types

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> TupleExpressionParserInfo:
        assert isinstance(self._parser_info, TupleExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSameType(
        self,
        other: GenericType,
    ) -> bool:
        return (
            isinstance(other, GenericTupleType)
            and len(self.generic_types) == len(other.generic_types)
            and all(
                this_type.IsSameType(that_type)
                for this_type, that_type in zip(self.generic_types, other.generic_types)
            )
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConcreteTypeImpl(self) -> ConcreteType:
        return ConcreteTupleType(
            self.parser_info,
            [
                generic_type.CreateConcreteType(parser_info)
                for generic_type, parser_info in zip(self.generic_types, self.parser_info.types)
            ],
        )


# ----------------------------------------------------------------------
class ConcreteTupleType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: TupleExpressionParserInfo,
        concrete_types: List[ConcreteType],
    ):
        super(ConcreteTupleType, self).__init__(parser_info)

        self.concrete_types                 = concrete_types

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> TupleExpressionParserInfo:
        assert isinstance(self._parser_info, TupleExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
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
    def _CreateConstrainedTypeImpl(self) -> "ConstrainedTupleType":
        constrained_types: List[ConstrainedType] = []
        errors: List[Error] = []

        for concrete_type in self.concrete_types:
            try:
                constrained_types.append(concrete_type.CreateConstrainedType())
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        return ConstrainedTupleType(self, constrained_types)


# ----------------------------------------------------------------------
class ConstrainedTupleType(ConstrainedType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        concrete_type: ConcreteTupleType,
        constrained_types: List[ConstrainedType],
    ):
        super(ConstrainedTupleType, self).__init__(concrete_type)

        self.constrained_types              = constrained_types
