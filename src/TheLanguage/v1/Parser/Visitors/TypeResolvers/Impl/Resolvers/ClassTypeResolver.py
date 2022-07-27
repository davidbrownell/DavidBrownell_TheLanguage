# ----------------------------------------------------------------------
# |
# |  ClassTypeResolver.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-25 09:51:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassTypeResolver object"""

import os

from typing import Dict, Generator, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...StatementTypeResolver import CompileTimeInfo, StatementTypeResolver
    from ...TypeResolver import TypeResolver

    from ...Impl import MatchConstraintCall

    from ....Namespaces import Namespace, ParsedNamespace

    from .....ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from .....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from .....ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from .....ParserInfos.Statements.StatementParserInfo import StatementParserInfo
    from .....ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from .....ParserInfos.Types.ClassTypes.ConcreteClassType import ClassStatementParserInfo, ConcreteClassType, TypeResolver as ConcreteClassTypeResolver
    from .....ParserInfos.Types.ClassTypes.GenericClassType import GenericClassType
    from .....ParserInfos.Types.FuncDefinitionTypes.GenericFuncDefinitionType import GenericFuncDefinitionType

    from .....ParserInfos.Types.ConcreteType import ConcreteType
    from .....ParserInfos.Types.ConstrainedType import ConstrainedType
    from .....ParserInfos.Types.GenericType import GenericType


# ----------------------------------------------------------------------
class ClassTypeResolver(StatementTypeResolver):
    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(
        self,
        compile_time_info: List[Dict[str, CompileTimeInfo]],
    ) -> "ClassTypeResolver":
        return ClassTypeResolver(
            self.namespace,
            self.fundamental_namespace,
            compile_time_info,
            self.root_resolvers,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConcreteTypeImpl(
        self,
        updated_type_resolver: StatementTypeResolver,
    ) -> ConcreteType:
        # ----------------------------------------------------------------------
        class ResolverAdapter(ConcreteClassTypeResolver):
            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def EvalConcreteType(
                parser_info: ExpressionParserInfo,
                *,
                no_finalize=False,
            ) -> ConcreteType:
                return updated_type_resolver.EvalConcreteType(parser_info, no_finalize=no_finalize)

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def CreateGenericType(
                parser_info: StatementParserInfo,
            ) -> GenericType:
                for nested_namespace_or_namespaces in updated_type_resolver.namespace.EnumChildren():
                    if isinstance(nested_namespace_or_namespaces, list):
                        nested_namespaces = nested_namespace_or_namespaces
                    else:
                        nested_namespaces = [nested_namespace_or_namespaces, ]

                    for nested_namespace in nested_namespaces:
                        assert isinstance(nested_namespace, ParsedNamespace), nested_namespace

                        if nested_namespace.parser_info is parser_info:
                            nested_resolver = updated_type_resolver.GetOrCreateNestedResolver(nested_namespace)

                            if isinstance(parser_info, ClassStatementParserInfo):
                                return _GenericClassType(parser_info, nested_resolver)
                            elif isinstance(parser_info, FuncDefinitionStatementParserInfo):
                                return _GenericFuncDefinitionType(parser_info, nested_resolver)
                            elif isinstance(parser_info, TypeAliasStatementParserInfo):
                                return _GenericTypeAliasType(parser_info, nested_resolver)
                            else:
                                assert False, parser_info  # pragma: no cover

                assert False, parser_info  # pragma: no cover

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def EvalStatements(
                statements: List[StatementParserInfo],
            ) -> None:
                updated_type_resolver.EvalStatements(statements)

            # ----------------------------------------------------------------------
            @staticmethod
            @Interface.override
            def ValidateDefaultInitialization(
                generic_type: GenericType,
            ) -> None:
                if not isinstance(generic_type, _GenericTypeMixin):
                    BugBug = 10

                assert isinstance(generic_type, _GenericTypeMixin), generic_type
                generic_type.ValidateDefaultInitialization()

        # ----------------------------------------------------------------------

        assert isinstance(self.namespace.parser_info, ClassStatementParserInfo), self.namespace.parser_info

        return ConcreteClassType(self.namespace.parser_info, ResolverAdapter())


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@Interface.mixin
class _GenericTypeMixin(Interface.Interface):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        resolver: StatementTypeResolver,
    ):
        self._resolver                      = resolver

    # ----------------------------------------------------------------------
    def ValidateDefaultInitialization(self) -> None:
        self._resolver.ValidateDefaultInitialization()

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> ConcreteType:
        return self._resolver.CreateConcreteType(parser_info)


# ----------------------------------------------------------------------
class _GenericClassType(_GenericTypeMixin, GenericClassType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: ClassStatementParserInfo,
        resolver: StatementTypeResolver,
    ):
        GenericClassType.__init__(self, parser_info)
        _GenericTypeMixin.__init__(self, resolver)


# ----------------------------------------------------------------------
class _GenericFuncDefinitionType(_GenericTypeMixin, GenericFuncDefinitionType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: FuncDefinitionStatementParserInfo,
        resolver: StatementTypeResolver,
    ):
        GenericFuncDefinitionType.__init__(self, parser_info)
        _GenericTypeMixin.__init__(self, resolver)


# ----------------------------------------------------------------------
class _GenericTypeAliasType(_GenericTypeMixin, GenericType):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: TypeAliasStatementParserInfo,
        resolver: StatementTypeResolver,
    ):
        GenericType.__init__(self, parser_info)
        _GenericTypeMixin.__init__(self, resolver)

    # ----------------------------------------------------------------------
    @property
    @Interface.override
    def parser_info(self) -> TypeAliasStatementParserInfo:
        assert isinstance(self._parser_info, TypeAliasStatementParserInfo), self._parser_info
        return self._parser_info

    # ----------------------------------------------------------------------
    @Interface.override
    def IsSameType(
        self,
        other: GenericType,
    ) -> bool:
        # BugBug: Not sure how to implement this right now
        return False
