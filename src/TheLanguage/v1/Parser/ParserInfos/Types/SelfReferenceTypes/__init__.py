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
    from ..GenericType import GenericType

    from ...Expressions.SelfReferenceExpressionParserInfo import ExpressionParserInfo, SelfReferenceExpressionParserInfo

    from ...Types.ConcreteType import ConcreteType
    from ...Types.ConstrainedType import ConstrainedType


# ----------------------------------------------------------------------
class SelfReferenceGenericType(GenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: SelfReferenceExpressionParserInfo,
    ):
        super(SelfReferenceGenericType, self).__init__(parser_info, is_default_initializable=True)

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> SelfReferenceExpressionParserInfo:
        assert isinstance(self._parser_info, SelfReferenceExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        expression_parser_info: ExpressionParserInfo,
    ) -> ConcreteType:
        assert expression_parser_info is self.parser_info, (expression_parser_info, self.parser_info)
        return SelfReferenceConcreteType(self.parser_info)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> ConcreteType:
        return self.CreateConcreteType(self.parser_info)


# ----------------------------------------------------------------------
class SelfReferenceConcreteType(ConcreteType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: SelfReferenceExpressionParserInfo,
    ):
        super(SelfReferenceConcreteType, self).__init__(parser_info, is_default_initializable=True)

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> SelfReferenceExpressionParserInfo:
        assert isinstance(self._parser_info, SelfReferenceExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def IsCovariant(
        self,
        other: ConcreteType,
    ) -> bool:
        return (
            isinstance(other, SelfReferenceConcreteType)
            and self.parser_info.mutability_modifier == other.parser_info.mutability_modifier
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
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
    def _CreateConstrainedTypeImpl(
        self,
        expression_parser_info: ExpressionParserInfo,
    ) -> "SelfReferenceConstrainedType":
        assert expression_parser_info is self.parser_info, (expression_parser_info, self.parser_info)
        return SelfReferenceConstrainedType(self, self.parser_info.mutability_modifier)

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConstrainedTypeImpl(self) -> "SelfReferenceConstrainedType":
        return self._CreateConstrainedTypeImpl(self.parser_info)


# ----------------------------------------------------------------------
class SelfReferenceConstrainedType(ConstrainedType):
    pass
