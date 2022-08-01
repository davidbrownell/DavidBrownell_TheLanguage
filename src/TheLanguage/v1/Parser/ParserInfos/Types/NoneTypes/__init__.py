# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-26 16:59:16
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains None-related types"""

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

    from ...Expressions.NoneExpressionParserInfo import ExpressionParserInfo, NoneExpressionParserInfo

    from ...Types.ConcreteType import ConcreteType
    from ...Types.ConstrainedType import ConstrainedType


# ----------------------------------------------------------------------
class NoneGenericType(GenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: NoneExpressionParserInfo,
    ):
        super(NoneGenericType, self).__init__(parser_info, True)

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> NoneExpressionParserInfo:
        assert isinstance(self._parser_info, NoneExpressionParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateBoundGenericType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> BoundGenericType:
        assert parser_info is self.parser_info, (parser_info, self.parser_info)
        return NoneBoundGenericType(self)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateDefaultConcreteTypeImpl(self) -> ConcreteType:
        return self.CreateBoundGenericType(self.parser_info).CreateConcreteType()


# ----------------------------------------------------------------------
class NoneBoundGenericType(BoundGenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        generic_type: NoneGenericType,
    ):
        super(NoneBoundGenericType, self).__init__(generic_type, generic_type.parser_info)

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(self) -> ConcreteType:
        return ConcreteNoneType(self.generic_type.parser_info)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsCovariant(
        other: BoundGenericType,
    ) -> bool:
        return isinstance(other, NoneBoundGenericType)


# ----------------------------------------------------------------------
class ConcreteNoneType(ConcreteType):
    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> NoneExpressionParserInfo:
        assert isinstance(self._parser_info, NoneExpressionParserInfo), self._parser_info
        return self._parser_info

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
    def _CreateConstrainedTypeImpl(self) -> "ConstrainedNoneType":
        return ConstrainedNoneType(self)


# ----------------------------------------------------------------------
class ConstrainedNoneType(ConstrainedType):
    pass
