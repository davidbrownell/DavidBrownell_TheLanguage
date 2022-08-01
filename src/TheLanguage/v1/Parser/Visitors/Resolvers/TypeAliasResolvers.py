# ----------------------------------------------------------------------
# |
# |  TypeAliasResolvers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-28 13:32:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains Resolvers that have knowledge of type aliases"""

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

    # BugBug from .Impl.ConcreteTypeResolver import ConcreteTypeResolver
    # BugBug from .Impl.GenericTypeResolver import GenericTypeResolver
    # BugBug from .Impl.GenericTypeImpl import GenericStatementTypeMixin

    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...ParserInfos.Types.ConcreteType import ConcreteType
    from ...ParserInfos.Types.GenericTypes import BoundGenericType


# ----------------------------------------------------------------------
class TypeAliasGenericType(GenericType[TypeAliasStatementParserInfo]):
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def _CreateConcreteData(
        updated_resolver: TypeResolver,
    ) -> Any:
        assert isinstance(updated_resolver.namespace.parser_info, TypeAliasStatementParserInfo), updated_resolver.namespace.parser_info
        return updated_resolver.EvalConcreteType(updated_resolver.namespace.parser_info.type)

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateBoundGenericType(
        self,
        concrete_data: Any,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> BoundGenericType:
        return _TypeAliasBoundGenericType(concrete_data, self, parser_info)


# ----------------------------------------------------------------------
class _TypeAliasBoundGenericType(BoundGenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        concrete_data: Any,
        generic_type: GenericType,
        expression_parser_info: FuncOrTypeExpressionParserInfo,
    ):
        assert isinstance(concrete_data, ConcreteType), concrete_data

        super(_TypeAliasBoundGenericType, self).__init__(generic_type, expression_parser_info)

        self._concrete_type                 = concrete_data

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(self) -> ConcreteType:
        pass # BugBug return self._type_resolver.EvalConcreteType(self.expression_parser_info)

    # ----------------------------------------------------------------------
    @Interface.override
    def IsCovariant(
        self,
        other: BoundGenericType,
    ) -> bool:
        return False # BugBug


# BugBug # ----------------------------------------------------------------------
# BugBug class TypeAliasGenericTypeResolver(GenericTypeResolver):
# BugBug     # ----------------------------------------------------------------------
# BugBug     def __init__(self, *args, **kwargs):
# BugBug         super(TypeAliasGenericTypeResolver, self).__init__(
# BugBug             _TypeAliasGenericStatementType,
# BugBug             *args,
# BugBug             **kwargs,
# BugBug         )
# BugBug
# BugBug     # ----------------------------------------------------------------------
# BugBug     # ----------------------------------------------------------------------
# BugBug     # ----------------------------------------------------------------------
# BugBug     @Interface.override
# BugBug     def _CreateConcreteTypeImpl(
# BugBug         self,
# BugBug         updated_resolver: ConcreteTypeResolver,
# BugBug     ) -> ConcreteType:
# BugBug         assert isinstance(self.namespace.parser_info, TypeAliasStatementParserInfo), self.namespace.parser_info
# BugBug         return updated_resolver.EvalConcreteType(self.namespace.parser_info.type)
# BugBug
# BugBug
# BugBug # ----------------------------------------------------------------------
# BugBug # ----------------------------------------------------------------------
# BugBug # ----------------------------------------------------------------------
# BugBug class _TypeAliasGenericStatementType(GenericStatementTypeMixin[TypeAliasStatementParserInfo]):
# BugBug     # ----------------------------------------------------------------------
# BugBug     @Interface.override
# BugBug     def IsCovariant(
# BugBug         self,
# BugBug         other: GenericType,
# BugBug     ) -> bool:
# BugBug         return False # BugBug
# BugBug
