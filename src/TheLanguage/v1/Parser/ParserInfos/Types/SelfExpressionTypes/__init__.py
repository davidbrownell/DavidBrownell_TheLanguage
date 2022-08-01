# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-29 14:03:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains SelfExpression-related types"""

import os

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GenericTypes import BoundGenericType, GenericType

    from ...Expressions.SelfReferenceExpressionParserInfo import SelfReferenceExpressionParserInfo

    from ...Types.ConcreteType import ConcreteType
    from ...Types.ConstrainedType import ConstrainedType


# ----------------------------------------------------------------------
class SelfExpressionGenericType(GenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: SelfReferenceExpressionParserInfo,
    ):
        super(SelfExpressionGenericType, self).__init__(parser_info, True)

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> SelfReferenceExpressionParserInfo:
        assert isinstance(self._parser_info, SelfReferenceExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateBoundGenericType(
        self,
        parser_info: SelfReferenceExpressionParserInfo,
    ) -> BoundGenericType:
        assert parser_info is self.parser_info, (parser_info, self.parser_info)
        return SelfExpressionBoundGenericType(self)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> ConcreteType:
        return self.CreateBoundGenericType(self.parser_info).CreateConcreteType()


# ----------------------------------------------------------------------
class SelfExpressionBoundGenericType(BoundGenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        generic_type: SelfExpressionGenericType,
    ):
        super(SelfExpressionBoundGenericType, self).__init__(generic_type, generic_type.parser_info)

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(self) -> ConcreteType:
        return ConcreteSelfReferenceType(self.generic_type.parser_info)

    # ----------------------------------------------------------------------
    @Interface.override
    def IsCovariant(
        self,
        other: GenericType,
    ) -> bool:
        return (
            isinstance(other, SelfExpressionBoundGenericType)
            and self.generic_type.parser_info.mutability_modifier == other.generic_type.parser_info.mutability_modifier
        )


# ----------------------------------------------------------------------
class ConcreteSelfReferenceType(ConcreteType):
    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> SelfReferenceExpressionParserInfo:
        assert isinstance(self._parser_info, SelfReferenceExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass3Impl(self) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass4Impl(self) -> None:
        # Nothing to do here
        pass

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(self) -> "ConstrainedSelfReferenceType":
        return ConstrainedSelfReferenceType(self)


# ----------------------------------------------------------------------
class ConstrainedSelfReferenceType(ConstrainedType):
    pass
