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

from contextlib import ExitStack
from enum import auto, Flag
from typing import Dict, Generator, List, Optional, Tuple, Union

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
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodType
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo

    from ...ParserInfos.Statements.ConcreteInfo.ConcreteClass import ConcreteClass
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Traits.NamedTrait import NamedTrait
    from ...ParserInfos.Types import ClassType, NoneType, Type, TupleType, VariantType

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
class EntityResolverMixin(EntityResolver, BaseMixin):
    # ----------------------------------------------------------------------
    @Interface.override
    def ResolveMiniLanguageType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageType:
        assert self._context_stack

        mini_language_type = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._context_stack[-1].compile_time_info,
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
        assert self._context_stack

        return MiniLanguageHelpers.EvalExpression(
            parser_info,
            self._context_stack[-1].compile_time_info,
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
        assert self._context_stack

        type_expression = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._context_stack[-1].compile_time_info,
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

            resolved_parser_info: Union[
                None,
                ClassStatementParserInfo,
                TypeAliasStatementParserInfo,
            ] = None

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

            result = self.CreateConcreteType(
                resolved_parser_info,
                type_expression.templates,
            )

            # BugBug: Process the constraints

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
    def CreateConcreteType(
        self,
        parser_info: Union[ClassStatementParserInfo, TypeAliasStatementParserInfo],
        template_arguments: Optional[TemplateArgumentsParserInfo],
    ) -> Type:
        assert self._context_stack

        was_cached, get_or_create_result = parser_info.GetOrCreateConcreteEntityFactory(
            template_arguments,
            self,
        )

        if was_cached:
            assert isinstance(get_or_create_result, Type), get_or_create_result
            return get_or_create_result

        assert (
            isinstance(get_or_create_result, tuple)
            and len(get_or_create_result) == 2
        ), get_or_create_result

        resolved_template_arguments, init_concrete_entity = get_or_create_result

        # Determine the foundational set of compile time information to use
        if parser_info.translation_unit__ != self._context_stack[-1].parser_info.translation_unit__:
            compile_time_info = [self._configuration_info, ]
        else:
            compile_time_info = self._context_stack[-1].compile_time_info

        # Add the template arguments (if necessary)
        if resolved_template_arguments is not None:
            new_compile_time_info: Dict[str, CompileTimeInfo] = {}

            # Add the types
            # BugBug

            # Add the decorators
            for decorator_param, decorator_arg in resolved_template_arguments.decorators:
                assert decorator_param.name not in new_compile_time_info, decorator_param.name

                new_compile_time_info[decorator_param.name] = CompileTimeInfo(
                    decorator_arg.type,
                    decorator_arg.value,
                )

            compile_time_info = compile_time_info + [new_compile_time_info, ]

        # Update the context and create the type
        result: Optional[Type] = None

        with ExitStack() as exit_stack:
            self._context_stack.append(
                self.__class__._Context(  # pylint: disable=protected-access
                    parser_info,
                    compile_time_info,
                ),
            )

            exit_stack.callback(self._context_stack.pop)

            entity = init_concrete_entity()
            assert isinstance(entity, Type), entity

            result = entity

            # Evaluate the template if there is a corresponding method
            if (
                isinstance(result, ClassType)
                and SpecialMethodType.EvalTemplates in result.concrete_class.special_methods
            ):
                statements = result.concrete_class.special_methods[SpecialMethodType.EvalTemplates].statements
                assert statements is not None

                for statement in statements:
                    if statement.is_disabled__:
                        continue

                    assert isinstance(statement, FuncInvocationStatementParserInfo), statement

                    eval_result = MiniLanguageHelpers.EvalExpression(
                        statement.expression,
                        compile_time_info,
                        self._TypeCheckHelper,
                    )

                    assert isinstance(eval_result.type, MiniLanguageHelpers.NoneType), eval_result

        assert result is not None
        return result

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

        assert self._context_stack
        context_parser_info = self._context_stack[-1].parser_info
        assert isinstance(context_parser_info, NamedTrait), context_parser_info

        # ----------------------------------------------------------------------
        def EnumNamespaces() -> Generator[Namespace, None, None]:
            namespace = context_parser_info.namespace__

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

            if (
                namespace.parser_info.translation_unit__ == context_parser_info.translation_unit__
                and namespace.parser_info.IsNameOrdered(context_parser_info.namespace__.scope_flag)
                and namespace.ordered_id > context_parser_info.namespace__.ordered_id
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
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _TypeCheckHelper(
        self,
        type_name: str,
        operator: TypeCheckExpressionOperatorType,
        type_parser_info: ExpressionParserInfo,
    ) -> bool:
        assert False, "BugBug: TODO"
        return False
