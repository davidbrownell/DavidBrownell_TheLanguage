# ----------------------------------------------------------------------
# |
# |  ClassResolvers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 13:14:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains Resolvers that have knowledge of classes"""

import os

from typing import Any

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl.GenericTypeResolver import GenericType
    from .Impl.TypeResolver import TypeResolver

    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo

    from ...ParserInfos.Types.ConcreteType import ConcreteType
    from ...ParserInfos.Types.GenericTypes import BoundGenericType

    from ...ParserInfos.Types.ClassTypes.ConcreteClassType import ConcreteClassType


# ----------------------------------------------------------------------
class ClassGenericType(GenericType[ClassStatementParserInfo]):
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _CreateConcreteData(
        updated_resolver: TypeResolver,
    ) -> Any:
        assert isinstance(updated_resolver.namespace.parser_info, ClassStatementParserInfo), updated_resolver.namespace.parser_info
        return ConcreteClassType(updated_resolver, updated_resolver.namespace.parser_info)

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateBoundGenericType(
        self,
        concrete_data: Any,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> BoundGenericType:
        return _ClassBoundGenericType(concrete_data, self, parser_info)


# ----------------------------------------------------------------------
class _ClassBoundGenericType(BoundGenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        concrete_data: Any,
        generic_type: GenericType,
        expression_parser_info: FuncOrTypeExpressionParserInfo,
    ):
        super(_ClassBoundGenericType, self).__init__(generic_type, expression_parser_info)

        self._concrete_data                 = concrete_data

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(self) -> ConcreteType:
        pass # BugBug concrete_type = ConcreteClassType(self._type_resolver, self.generic_type.parser_info)
        pass # BugBug
        pass # BugBug return concrete_type

    # ----------------------------------------------------------------------
    @Interface.override
    def IsCovariant(
        self,
        other: BoundGenericType,
    ) -> bool:
        return False # BugBug
