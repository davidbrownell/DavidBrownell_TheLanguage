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
    from ..GenericTypes import GenericExpressionType, GenericType

    from ...Expressions.SelfReferenceExpressionParserInfo import SelfReferenceExpressionParserInfo

    from ...Types.ConcreteType import ConcreteType
    from ...Types.ConstrainedType import ConstrainedType


# ----------------------------------------------------------------------
class GenericSelfExpressionType(GenericExpressionType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: SelfReferenceExpressionParserInfo,
    ):
        super(GenericSelfExpressionType, self).__init__(parser_info, True)

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> SelfReferenceExpressionParserInfo:
        assert isinstance(self._parser_info, SelfReferenceExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSameType(
        self,
        other: GenericType,
    ) -> bool:
        return False # BugBug

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConcreteTypeImpl(self) -> ConcreteType:
        return ConcreteSelfReferenceType(self.parser_info)


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
