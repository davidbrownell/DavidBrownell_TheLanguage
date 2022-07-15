# ----------------------------------------------------------------------
# |
# |  EntityResolverMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-07 11:07:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the EntityResolverMixin object"""

import os
import threading

from contextlib import ExitStack
from enum import auto, Flag
from typing import Any, Callable, cast, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ..Namespaces import Namespace, ParsedNamespace

    from ...ParserInfos.ParserInfo import CompileTimeInfo

    from ...ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo
    from ...ParserInfos.Common.TemplateParametersParserInfo import ResolvedTemplateArguments

    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier

    from ...ParserInfos.EntityResolver import EntityResolver

    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo, ParserInfo
    from ...ParserInfos.Expressions.NestedTypeExpressionParserInfo import NestedTypeExpressionParserInfo
    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.TypeCheckExpressionParserInfo import OperatorType as TypeCheckExpressionOperatorType
    from ...ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodType
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo

    from ...ParserInfos.Statements.ConcreteClass import ConcreteClass
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Traits.NamedTrait import NamedTrait
    from ...ParserInfos.Types import ClassType, ConcreteType, NoneType, Type, TupleType, VariantType

    from ...Common import MiniLanguageHelpers
    from ...Error import CreateError, ErrorException
    from ...TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
UnexpectedStandardTypeError                 = CreateError(
    "A standard type was not expected in this context",
)

UnexpectedMiniLanguageTypeError             = CreateError(
    "A compile-time type was not expected in this context",
)

InvalidNamedTypeError                       = CreateError(
    "'{name}' is not a recognized type",
    name=str,
)

InvalidTypeReferenceError                   = CreateError(
    "'{name}' is defined via an ordered statement; it can only be used after it is defined",
    name=str,
    defined_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
class StandardResolveFlag(Flag):
    Namespace                               = auto()
    CompileTimeInfo                         = auto()
    Nested                                  = auto()

    All                                     = Namespace | CompileTimeInfo | Nested


# ----------------------------------------------------------------------
class EntityResolverMixin(BaseMixin):
    # ----------------------------------------------------------------------
    def CreateConcreteTypeFactory(
        self,
        parser_info: StatementParserInfo,
    ) -> Callable[
        [
            Optional[TemplateArgumentsParserInfo],
        ],
        ConcreteType,
    ]:
        assert isinstance(parser_info, TemplatedStatementTrait), parser_info
        assert self._root_statement_parser_info is not None

        resolver = _EntityResolver(
            self._root_statement_parser_info,
            self._compile_time_info,
            self._compile_time_info,
            self._fundamental_types_namespace,
        )

        return parser_info.CreateConcreteTypeFactory(resolver)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _EntityResolver(EntityResolver):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info: StatementParserInfo,
        compile_time_info: List[Dict[str, CompileTimeInfo]],
        original_compile_time_info: List[Dict[str, CompileTimeInfo]],
        fundamental_types_namespace: Optional[Namespace],
    ):
        self._parser_info                   = parser_info
        self._compile_time_info             = compile_time_info
        self._original_compile_time_info    = original_compile_time_info
        self._fundamental_types_namespace   = fundamental_types_namespace

    # ----------------------------------------------------------------------
    @Interface.override
    def Clone(self) -> EntityResolver:
        return self.__class__(
            self._parser_info,
            self._compile_time_info,
            self._original_compile_time_info,
            self._fundamental_types_namespace,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ResolveMiniLanguageType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageType:
        mini_language_type = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._compile_time_info,
            self._TypeCheckHelper,
        )

        if isinstance(mini_language_type, ExpressionParserInfo):
            raise ErrorException(
                UnexpectedStandardTypeError.Create(
                    region=mini_language_type.regions__.self__,
                ),
            )

        return mini_language_type

    # ----------------------------------------------------------------------
    @Interface.override
    def ResolveMiniLanguageExpression(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageExpression.EvalResult:
        return MiniLanguageHelpers.EvalExpression(
            parser_info,
            self._compile_time_info,
            self._TypeCheckHelper,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ResolveType(
        self,
        parser_info: ExpressionParserInfo,
        *,
        resolve_aliases: bool=False,
        resolve_flag: StandardResolveFlag=StandardResolveFlag.All,
    ) -> Type:
        type_expression = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._compile_time_info,
            self._TypeCheckHelper,
        )

        if isinstance(type_expression, MiniLanguageHelpers.MiniLanguageType):
            raise ErrorException(
                UnexpectedMiniLanguageTypeError.Create(
                    region=parser_info.regions__.self__,
                ),
            )

        elif isinstance(type_expression, FuncOrTypeExpressionParserInfo):
            assert isinstance(type_expression.value, str), type_expression.value

            resolved_parser_info: Optional[ParserInfo] = None

            if resolved_parser_info is None and resolve_flag & StandardResolveFlag.Nested:
                resolved_parser_info = self._ResolveByNested(type_expression)

            if resolved_parser_info is None and resolve_flag & StandardResolveFlag.Namespace:
                resolved_parser_info = self._ResolveByNamespace(type_expression)

            if resolved_parser_info is None:
                raise ErrorException(
                    InvalidNamedTypeError.Create(
                        region=type_expression.regions__.value,
                        name=type_expression.value,
                    ),
                )

            if isinstance(resolved_parser_info, TemplatedStatementTrait):
                concrete_type_factory = resolved_parser_info.CreateConcreteTypeFactory(self)

                result = concrete_type_factory(type_expression.templates)

                # BugBug: Process the constraints

            else:
                assert False, "BugBug"

                # TODO: Error if templates
                # TODO: Error if constraints

            if resolve_aliases:
                result = result.ResolveAliases()

            return result

        elif isinstance(type_expression, NestedTypeExpressionParserInfo):
            raise NotImplementedError("TODO: NestedTypeExpressionParserInfo")

        elif isinstance(type_expression, NoneExpressionParserInfo):
            return NoneType(type_expression)

        elif isinstance(type_expression, TupleExpressionParserInfo):
            return TupleType(
                type_expression,
                [
                    self.ResolveType(child_type)
                    for child_type in type_expression.types
                ],
            )

        elif isinstance(type_expression, VariantExpressionParserInfo):
            return VariantType(
                type_expression,
                [
                    self.ResolveType(child_type)
                    for child_type in type_expression.types
                ],
            )

        else:
            assert False, type_expression  # pragma: no cover

    # ----------------------------------------------------------------------
    @Interface.override
    def CreateConcreteType(
        self,
        parser_info: StatementParserInfo,
        resolved_template_arguments: Optional[ResolvedTemplateArguments],
        create_type_func: Callable[[EntityResolver], ConcreteType],
    ) -> ConcreteType:
        if parser_info.translation_unit__ == self._parser_info.translation_unit__:
            compile_time_info = self._compile_time_info
        else:
            compile_time_info = self._original_compile_time_info

        if resolved_template_arguments is not None:
            new_compile_time_info_item: Dict[str, CompileTimeInfo] = {}

            # Add the types
            # BugBug

            # Add the decorators
            for decorator_param, decorator_arg in resolved_template_arguments.decorators:
                assert decorator_param.name not in new_compile_time_info_item, decorator_param.name

                new_compile_time_info_item[decorator_param.name] = CompileTimeInfo(
                    decorator_arg.type,
                    decorator_arg.value,
                )

            compile_time_info = compile_time_info + [new_compile_time_info_item, ]

        updated_resolver = self.__class__(
            parser_info,
            compile_time_info,
            self._original_compile_time_info,
            self._fundamental_types_namespace,
        )

        return create_type_func(updated_resolver)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _ResolveByNested(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> Union[
        None,
        ClassStatementParserInfo,
        TypeAliasStatementParserInfo,
    ]:
        assert isinstance(parser_info.value, str), parser_info.value
        return None # BugBug

    # ----------------------------------------------------------------------
    def _ResolveByNamespace(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> Union[
        None,
        ClassStatementParserInfo,
        TypeAliasStatementParserInfo,
    ]:
        assert isinstance(parser_info.value, str), parser_info.value
        assert isinstance(self._parser_info, NamedTrait), self._parser_info

        # ----------------------------------------------------------------------
        def EnumNamespaces() -> Generator[Namespace, None, None]:
            assert isinstance(self._parser_info, NamedTrait), self._parser_info
            namespace = self._parser_info.namespace__

            # BugBUg: Clean up this loop once the quirks have been worked out
            while True:
                assert namespace is not None

                if namespace.name is None:
                    break

                yield namespace

                namespace = namespace.parent

            if self._fundamental_types_namespace:
                yield self._fundamental_types_namespace

        # ----------------------------------------------------------------------

        for namespace in EnumNamespaces():
            namespace = namespace.GetChild(parser_info.value)
            if namespace is None:
                continue

            assert isinstance(namespace, ParsedNamespace), namespace
            if isinstance(namespace.parser_info, RootStatementParserInfo):
                continue

            if (
                namespace.parser_info.translation_unit__ == self._parser_info.translation_unit__
                and namespace.parser_info.IsNameOrdered(self._parser_info.namespace__.scope_flag)
                and namespace.ordered_id > self._parser_info.namespace__.ordered_id
            ):
                raise ErrorException(
                    InvalidTypeReferenceError.Create(
                        region=parser_info.regions__.value,
                        name=parser_info.value,
                        defined_region=namespace.parser_info.regions__.self__,
                    ),
                )

            namespace = namespace.ResolveImports()

            assert isinstance(
                namespace.parser_info,
                (
                    ClassStatementParserInfo,
                    TypeAliasStatementParserInfo,
                ),
            ), namespace.parser_info

            return namespace.parser_info

        return None

    # ----------------------------------------------------------------------
    def _TypeCheckHelper(
        self,
        type_name: str,
        operator: TypeCheckExpressionOperatorType,
        type_parser_info: ExpressionParserInfo,
    ) -> bool:
        assert False, "BugBug: TODO"
        return False
