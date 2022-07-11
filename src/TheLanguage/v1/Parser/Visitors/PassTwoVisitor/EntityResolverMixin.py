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

from typing import Dict, Optional, Union

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ..Namespaces import ParsedNamespace

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

    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Types import ConcreteClassType, NoneType, Type, TupleType, VariantType

    from ...Common import MiniLanguageHelpers
    from ...Error import CreateError, ErrorException


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
        mini_language_type = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._compile_time_stack,
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
            self._compile_time_stack,
            self._TypeCheckHelper,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def ResolveType(
        self,
        parser_info: ExpressionParserInfo,
        *,
        resolve_flag: StandardResolveFlag=StandardResolveFlag.All,
        resolve_aliases: bool=False,
    ) -> Type:
        type_expression = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._compile_time_stack,
            self._TypeCheckHelper,
        )

        if isinstance(type_expression, MiniLanguageHelpers.MiniLanguageType):
            raise ErrorException(
                UnexpectedMiniLanguageTypeError.Create(
                    region=parser_info.regions__.self__,
                ),
            )

        if isinstance(type_expression, FuncOrTypeExpressionParserInfo):
            # BugBug: Is it a template? If so, get the value from the compile time stack
            # and return early.

            assert isinstance(type_expression.value, str), type_expression.value

            resolved_parser_info: Union[
                None,
                ClassStatementParserInfo,
                TypeAliasStatementParserInfo,
            ] = None

            resolved_visibility: Optional[VisibilityModifier] = None
            resolved_is_class_member: Optional[bool] = None

            if resolved_parser_info is None and resolve_flag & StandardResolveFlag.CompileTimeInfo:
                pass # BugBug

            if resolved_parser_info is None and resolve_flag & StandardResolveFlag.Nested:
                pass # BugBug

            if resolved_parser_info is None and resolve_flag & StandardResolveFlag.Namespace:
                resolved_parser_info = self._ResolveNameByNamespace(type_expression.value)

                resolved_visibility = VisibilityModifier.public
                resolved_is_class_member = False

            if resolved_parser_info is None:
                raise ErrorException(
                    InvalidNamedTypeError.Create(
                        region=type_expression.regions__.value,
                        name=type_expression.value,
                    ),
                )

            assert resolved_visibility is not None
            assert resolved_is_class_member is not None

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

        assert False, type_expression  # pragma: no cover

    # ----------------------------------------------------------------------
    def CreateConcreteType(
        self,
        parser_info: TemplatedStatementTrait,
        template_arguments: Optional[TemplateArgumentsParserInfo],
    ) -> Type:
        is_cached_result, get_or_create_result = parser_info.GetOrCreateConcreteEntityFactory(
            template_arguments,
            self,
        )

        if is_cached_result:
            assert isinstance(get_or_create_result, Type), get_or_create_result
            return get_or_create_result

        assert isinstance(get_or_create_result, tuple), get_or_create_result
        assert len(get_or_create_result) == 2, get_or_create_result

        resolved_template_arguments, init_concrete_entity = get_or_create_result

        result: Optional[Type] = None

        with ExitStack() as exit_stack:
            if resolved_template_arguments is not None:
                new_compile_time_info: Dict[str, CompileTimeInfo] = {}

                # Add the types
                # BugBug

                # Add the decorators
                for decorator_parameter, decorator_result in resolved_template_arguments.decorators:
                    assert decorator_parameter.name not in new_compile_time_info, decorator_parameter.name

                    new_compile_time_info[decorator_parameter.name] = CompileTimeInfo(
                        decorator_result.type,
                        decorator_result.value,
                    )

                self._compile_time_stack.append(new_compile_time_info)
                exit_stack.callback(self._compile_time_stack.pop)

            entity = init_concrete_entity()

            assert isinstance(entity, Type), entity
            result = entity

            if (
                isinstance(result, ConcreteClassType)
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
                        self._compile_time_stack,
                        self._TypeCheckHelper,
                    )

                    assert isinstance(eval_result.type, MiniLanguageHelpers.NoneType), eval_result.type

        assert result is not None
        return result

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

    # ----------------------------------------------------------------------
    def _ResolveNameByNamespace(
        self,
        type_name: str,
    ) -> Union[
        None,
        ClassStatementParserInfo,
        TypeAliasStatementParserInfo,
    ]:
        assert self._namespaces_stack
        namespace_stack = self._namespaces_stack[-1]

        assert namespace_stack

        for namespace in reversed(namespace_stack):
            potential_namespace = namespace.GetChild(type_name)
            if potential_namespace is None:
                continue

            assert isinstance(potential_namespace, ParsedNamespace), potential_namespace
            resolved_namespace = potential_namespace.ResolveNamespace()

            assert isinstance(
                resolved_namespace.parser_info,
                (
                    ClassStatementParserInfo,
                    TypeAliasStatementParserInfo,
                ),
            ), resolved_namespace.parser_info

            return resolved_namespace.parser_info

        return None
