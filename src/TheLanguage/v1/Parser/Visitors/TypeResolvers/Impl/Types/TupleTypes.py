# ----------------------------------------------------------------------
# |
# |  TupleTypes.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-22 14:01:53
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

from typing import List

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .....Error import Error, ErrorException

    from .....ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo

    from .....ParserInfos.Types.ConcreteType import ConcreteType
    from .....ParserInfos.Types.ConstrainedType import ConstrainedType
    from .....ParserInfos.Types.GenericType import GenericType


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class GenericTupleType(GenericType):
    # ----------------------------------------------------------------------
    generic_types: List[GenericType]

    # ----------------------------------------------------------------------
    @property
    def parser_info(self) -> TupleExpressionParserInfo:
        result = super(GenericTupleType, self).parser_info
        assert isinstance(result, TupleExpressionParserInfo), result

        return result

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(self) -> "ConcreteTupleType":
        concrete_types: List[ConcreteType] = []
        errors: List[Error] = []

        for generic_type in self.generic_types:
            try:
                concrete_types.append(generic_type.CreateConcreteType())
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

        return ConcreteTupleType(self, concrete_types)


# ----------------------------------------------------------------------
@dataclass(frozen=True, eq=False)
class ConcreteTupleType(ConcreteType):
    # ----------------------------------------------------------------------
    concrete_types: List[ConcreteType]

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
@dataclass(frozen=True, eq=False)
class ConstrainedTupleType(ConstrainedType):
    # ----------------------------------------------------------------------
    constrained_types: List[ConstrainedType]
