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

    from ..NamespaceInfo import ParsedNamespaceInfo

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
        result = MiniLanguageHelpers.EvalType(
            parser_info,
            self._compile_time_stack,
            self._TypeCheckHelper,
        )

        if isinstance(result, ExpressionParserInfo):
            raise ErrorException(
                UnexpectedStandardTypeError.Create(
                    region=result.regions__.self__,
                ),
            )

        return result

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
    ) -> Type:
        resolved_type = MiniLanguageHelpers.EvalType(
            parser_info,
            self._compile_time_stack,
            self._TypeCheckHelper,
        )

        if isinstance(resolved_type, MiniLanguageHelpers.MiniLanguageType):
            raise ErrorException(
                UnexpectedMiniLanguageTypeError.Create(
                    region=parser_info.regions__.self__,
                ),
            )

        if isinstance(resolved_type, FuncOrTypeExpressionParserInfo):
            # BugBug: Is it a template? If so, get the value from the compile time stack
            # and return early.

            assert isinstance(resolved_type.value, str), resolved_type.value

            resolved_parser_info: Union[
                None,
                ClassStatementParserInfo,
                TypeAliasStatementParserInfo,
            ] = None

            resolved_visibility: Optional[VisibilityModifier] = None
            resolved_is_class_member: Optional[bool] = None

            if resolved_parser_info is None and resolve_flag & StandardResolveFlag.Namespace:
                resolved_parser_info = self._ResolveNameByNamespace(resolved_type.value)

                resolved_visibility = VisibilityModifier.public
                resolved_is_class_member = False

            if resolved_parser_info is None and resolve_flag & StandardResolveFlag.CompileTimeInfo:
                pass # BugBug

            if resolved_parser_info is None and resolve_flag & StandardResolveFlag.Nested:
                pass # BugBug

            if resolved_parser_info is None:
                raise ErrorException(
                    InvalidNamedTypeError.Create(
                        region=resolved_type.regions__.value,
                        name=resolved_type.value,
                    ),
                )

            assert resolved_visibility is not None
            assert resolved_is_class_member is not None

            result = self.CreateConcreteType(
                resolved_parser_info,
                resolved_type.templates,
            )

            # BugBug: Process the constraints

            return result

        elif isinstance(resolved_type, NestedTypeExpressionParserInfo):
            raise NotImplementedError("TODO: NestedTypeExpressionParserInfo")

        elif isinstance(resolved_type, NoneExpressionParserInfo):
            return NoneType(resolved_type)

        elif isinstance(resolved_type, TupleExpressionParserInfo):
            return TupleType(
                resolved_type,
                [
                    self.ResolveType(child_type)
                    for child_type in resolved_type.types
                ],
            )

        elif isinstance(resolved_type, VariantExpressionParserInfo):
            return VariantType(
                resolved_type,
                [
                    self.ResolveType(child_type)
                    for child_type in resolved_type.types
                ],
            )

        assert False, resolved_type  # pragma: no cover

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
            potential_namespace = namespace.children.get(type_name, None)
            if potential_namespace is None:
                continue

            assert isinstance(potential_namespace, ParsedNamespaceInfo), potential_namespace
            assert isinstance(
                potential_namespace.parser_info,
                (
                    ClassStatementParserInfo,
                    TypeAliasStatementParserInfo,
                ),
            ), potential_namespace.parser_info

            return potential_namespace.parser_info

        return None
