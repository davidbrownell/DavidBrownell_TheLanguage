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

from typing import Dict, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .RootTypeResolver import RootTypeResolver

    from ...StatementTypeResolver import CompileTimeInfo, StatementTypeResolver
    from ...TypeResolver import TypeResolver

    from ...Impl import MatchConstraintCall

    from ....Namespaces import Namespace, ParsedNamespace

    from .....ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from .....ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo

    from .....ParserInfos.Statements.StatementParserInfo import StatementParserInfo

    from .....ParserInfos.Types.ConcreteClass import ClassStatementParserInfo, ConcreteClass, TypeResolver as ConcreteClassTypeResolver

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
                for nested_namespace in updated_type_resolver.namespace.EnumChildren():
                    assert isinstance(nested_namespace, ParsedNamespace), nested_namespace

                    if nested_namespace.parser_info is parser_info:
                        return _GenericNestedType(
                            parser_info,
                            updated_type_resolver.GetOrCreateNestedResolver(nested_namespace),
                        )

                assert False, parser_info  # pragma: no cover

        # ----------------------------------------------------------------------

        assert isinstance(self.namespace.parser_info, ClassStatementParserInfo), self.namespace.parser_info

        return _ConcreteClassType(
            self.namespace.parser_info,
            ConcreteClass(
                self.namespace.parser_info,
                ResolverAdapter(),
            ),
        )


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _ConcreteClassType(ConcreteType):
    # ----------------------------------------------------------------------
    _concrete_class: ConcreteClass

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass1Impl(self) -> None:
        self._concrete_class.FinalizePass1()

    # ----------------------------------------------------------------------
    @Interface.override
    def _FinalizePass2Impl(self) -> None:
        self._concrete_class.FinalizePass2()

    # ----------------------------------------------------------------------
    @Interface.override
    def _CreateConstrainedTypeImpl(self) -> ConstrainedType:
        return self._concrete_class.CreateConstrainedType(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _GenericNestedType(GenericType):
    # ----------------------------------------------------------------------
    _resolver: StatementTypeResolver

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> ConcreteType:
        return self._resolver.CreateConcreteType(parser_info)
