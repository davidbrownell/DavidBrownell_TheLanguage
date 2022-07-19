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

    from ...ParserInfos.Common.ConstraintParametersParserInfo import ResolvedConstraintArguments
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

    from ...ParserInfos.Statements.Traits.ConstrainedStatementTrait import ConstrainedStatementTrait
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

InvalidVisibilityError                      = CreateError(
    "'{name}' exists, but is not visible in the current context",
    name=str,
    defined_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
class EntityResolverMixin(BaseMixin):
    # ----------------------------------------------------------------------
    def CreateConcreteTypeFactory(
        self,
        parser_info: StatementParserInfo,
    ) -> TemplatedStatementTrait.CreateConcreteTypeFactoryResultType:
        assert isinstance(parser_info, TemplatedStatementTrait), parser_info
        assert self._root_statement_parser_info is not None

        resolver = _EntityResolver.CreateAtRoot(
            self._root_statement_parser_info,
            self._configuration_info,
            self._fundamental_types_namespace,
        )

        return parser_info.CreateConcreteTypeFactory(resolver)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _EntityResolver(EntityResolver):
    # ----------------------------------------------------------------------
    @classmethod
    def CreateAtRoot(
        cls,
        parser_info: RootStatementParserInfo,
        configuration_info: Dict[str, CompileTimeInfo],
        fundamental_types_namespace: Optional[Namespace],
    ):
        return cls(
            [
                _EntityResolver._Context(
                    [configuration_info, ],
                    parser_info,
                    None,
                ),
            ],
            fundamental_types_namespace,
        )

    # ----------------------------------------------------------------------
    def __init__(
        self,
        context_stack: List["_EntityResolver._Context"],
        fundamental_types_namespace: Optional[Namespace],
    ):
        assert context_stack
        assert isinstance(context_stack[0].parser_info, RootStatementParserInfo), context_stack[0]

        # Get the most recent instantiated class
        instantiated_class: Optional[ClassType] = None

        for context_item in reversed(context_stack):
            if context_item.class_type is not None:
                instantiated_class = context_item.class_type
                break

        self._context_stack                 = context_stack
        self._instantiated_class            = instantiated_class
        self._fundamental_types_namespace   = fundamental_types_namespace

    # ----------------------------------------------------------------------
    @Interface.override
    def ResolveMiniLanguageType(
        self,
        parser_info: ExpressionParserInfo,
    ) -> MiniLanguageHelpers.MiniLanguageType:
        result = MiniLanguageHelpers.EvalTypeExpression(
            parser_info,
            self._context_stack[-1].compile_time_info,
            self._TypeCheckHelper,
        )

        # TODO: Make this more generic once all types support regions
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
    ) -> Type:
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
            if type_expression.IsResolved():
                return type_expression.resolved_type

            assert isinstance(type_expression.value, str), type_expression.value

            resolved_type: Optional[Type] = None

            for resolve_algo in [self._ResolveByNested, self._ResolveByNamespace]:
                create_concrete_type_func = resolve_algo(type_expression)
                if create_concrete_type_func is not None:
                    resolved_type = create_concrete_type_func(
                        type_expression.templates,
                        self._instantiated_class,
                    )
                    break

            if resolved_type is None:
                raise ErrorException(
                    InvalidNamedTypeError.Create(
                        region=type_expression.regions__.value,
                        name=type_expression.value,
                    ),
                )

            # Process the constraints
            if (
                isinstance(resolved_type.parser_info, ConstrainedStatementTrait)
                and resolved_type.parser_info.constraints is not None
            ):
                assert isinstance(resolved_type.parser_info, NamedTrait), resolved_type.parser_info

                resolved_constraint_arguments = resolved_type.parser_info.constraints.MatchCall(
                    resolved_type.parser_info.name,
                    resolved_type.parser_info.regions__.name,
                    type_expression.regions__.self__,
                    type_expression.constraints,
                    self,
                )

                # BugBug new_compile_time_info_item: Dict[str, CompileTimeInfo] = {}
                # BugBug
                # BugBug for constraint_param, constraint_arg in resolved_constraint_arguments.decorators:
                # BugBug     assert constraint_param.name not in new_compile_time_info_item, constraint_param.name
                # BugBug
                # BugBug     new_compile_time_info_item[constraint_param.name] = CompileTimeInfo(
                # BugBug         constraint_arg.type,
                # BugBug         constraint_arg.value,
                # BugBug     )
                # BugBug
                # BugBug
                # BugBug
                # BugBug # TODO:
                # BugBug # Note that constraints can only be validated once the class is fully formed.
                # BugBug # This means that they need to be validated when instances are instantiated.
                # BugBug #
                # BugBug # Move this code that that location once it is available.
                # BugBug
                # BugBug # Ensure that the constraints are valid (if necessary)
                # BugBug if (
                # BugBug     isinstance(resolved_type, ClassType)
                # BugBug     and SpecialMethodType.EvalConstraints in resolved_type.concrete_class.special_methods
                # BugBug ):
                # BugBug     # Temporarily add this to the compile time infos and validate
                # BugBug     with ExitStack() as exit_stack:
                # BugBug         self._context_stack[-1].compile_time_info.append(new_compile_time_info_item)
                # BugBug         exit_stack.callback(self._context_stack[-1].compile_time_info.pop)
                # BugBug
                # BugBug         self.EvalStatements(resolved_type.concrete_class.special_methods[SpecialMethodType.EvalConstraints].statement)

            else:
                if type_expression.constraints:
                    raise Exception("BugBug: Constraints where none were expected")

                resolved_constraint_arguments = None

            # We check to see if the expression is resolved above, but it is possible
            # that the resolution of its contained types resulted in the resolution of
            # itself (this is especially common with fundamental types).
            if type_expression.IsResolved():
                assert resolved_constraint_arguments == type_expression.resolved_constraint_arguments
                assert resolved_type == type_expression.resolved_type
            else:
                type_expression.Resolve(resolved_constraint_arguments, resolved_type)

            if resolve_aliases:
                resolved_type = resolved_type.ResolveAliases()

            return resolved_type

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
    def CreateConcreteTypeImpl(
        self,
        parser_info: StatementParserInfo,
        resolved_template_arguments: Optional[ResolvedTemplateArguments],
        instantiated_class: Optional[ClassType],
        create_type_func: Callable[[EntityResolver], Type],
    ) -> Type:
        # Determine the base set of compile time info to use when creating the type
        matching_context_index: Optional[int] = None

        if (
            self._instantiated_class is not None
            and parser_info.translation_unit__ == self._context_stack[-1].parser_info.translation_unit__
        ):
            assert isinstance(parser_info, NamedTrait), parser_info

            if isinstance(parser_info.namespace__.parent, ParsedNamespace):
                parent_parser_info = parser_info.namespace__.parent.parser_info

                for potential_matching_context_index in range(len(self._context_stack) - 1, 0, -1):
                    context_frame = self._context_stack[potential_matching_context_index]

                    if (
                        context_frame.class_type is not None
                        and context_frame.class_type.parser_info == parent_parser_info
                    ):
                        matching_context_index = potential_matching_context_index
                        break

        if matching_context_index is None:
            # Nothing matched. We can use the first context frame item as the context for this new item
            # even if they are from different translation units as the starting compile time info is
            # always the same.
            matching_context_index = 0

        is_complete_context_match = matching_context_index == len(self._context_stack) - 1

        result_type: Optional[Type] = None
        new_compile_time_info_item: Optional[Dict[str, CompileTimeInfo]] = None

        with ExitStack() as exit_stack:
            # Place the matching context on the stack
            if not is_complete_context_match:
                self._context_stack.append(self._context_stack[matching_context_index])
                exit_stack.callback(self._context_stack.pop)

            # Create a new frame item if necessary
            if resolved_template_arguments is not None:
                new_compile_time_info_item = {}

                # Add the types
                # BugBug

                # Add the decorators
                for decorator_param, decorator_arg in resolved_template_arguments.decorators:
                    assert decorator_param.name not in new_compile_time_info_item, decorator_param.name

                    new_compile_time_info_item[decorator_param.name] = CompileTimeInfo(
                        decorator_arg.type,
                        decorator_arg.value,
                    )

                # Add this item to the existing stack, but remove it once we are done
                self._context_stack[-1].compile_time_info.append(new_compile_time_info_item)
                exit_stack.callback(self._context_stack[-1].compile_time_info.pop)

            result_type = create_type_func(self)

        assert result_type is not None

        # Create a new resolver that is unique to this type.
        new_compile_time_info = self._context_stack[-1].compile_time_info

        if new_compile_time_info_item is not None:
            new_compile_time_info = new_compile_time_info + [new_compile_time_info_item, ]

        if isinstance(result_type, ClassType):
            context_result_type = result_type
            new_instantiated_class = instantiated_class or result_type
        else:
            context_result_type = None
            new_instantiated_class = instantiated_class

        new_context_item = _EntityResolver._Context(
            new_compile_time_info,
            parser_info,
            context_result_type,
        )

        new_resolver = _EntityResolver(
            self._context_stack[:matching_context_index + 1] + [new_context_item, ],
            self._fundamental_types_namespace,
        )

        result_type.Init(new_resolver, new_instantiated_class)

        return result_type

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _Context(object):
        # ----------------------------------------------------------------------
        compile_time_info: List[Dict[str, CompileTimeInfo]]
        parser_info: StatementParserInfo
        class_type: Optional[ClassType]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert isinstance(self.parser_info, NamedTrait), self.parser_info
            assert (
                (isinstance(self.parser_info, ClassStatementParserInfo) and self.class_type is not None)
                or self.class_type is None
            ), (self.parser_info, self.class_type)

    # ----------------------------------------------------------------------
    # |
    # |  Private Functions
    # |
    # ----------------------------------------------------------------------
    def _ResolveByNested(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> Optional[TemplatedStatementTrait.CreateConcreteTypeFactoryResultType]:
        assert isinstance(parser_info.value, str), parser_info.value

        for context in reversed(self._context_stack):
            if context.class_type is None:
                continue

            if not context.class_type.concrete_class.HasTypes():
                continue

            for dependency in context.class_type.concrete_class.types.EnumDependencies():
                visibility, type_info = dependency.ResolveDependencies()

                if type_info.name == parser_info.value:
                    assert isinstance(
                        type_info.statement,
                        (
                            ClassStatementParserInfo,
                            TypeAliasStatementParserInfo,
                        ),
                    ), type_info.statement

                    if visibility is None:
                        raise ErrorException(
                            InvalidVisibilityError.Create(
                                region=parser_info.regions__.self__,
                                name=parser_info.value,
                                defined_region=type_info.parser_info.regions__.self__,
                            ),
                        )

                    return type_info.concrete_type_factory_func

        return None

    # ----------------------------------------------------------------------
    def _ResolveByNamespace(
        self,
        parser_info: FuncOrTypeExpressionParserInfo,
    ) -> Optional[TemplatedStatementTrait.CreateConcreteTypeFactoryResultType]:
        assert isinstance(parser_info.value, str), parser_info.value

        reference_parser_info = self._context_stack[-1].parser_info
        assert isinstance(reference_parser_info, NamedTrait), reference_parser_info

        # ----------------------------------------------------------------------
        def EnumNamespaces() -> Generator[Namespace, None, None]:
            namespace = reference_parser_info.namespace__

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
                namespace.parser_info.translation_unit__ == parser_info.translation_unit__
                and namespace.parser_info.IsNameOrdered(reference_parser_info.namespace__.scope_flag)
                and namespace.parser_info.regions__.self__.begin > parser_info.regions__.self__.begin
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

            assert isinstance(namespace.parser_info, TemplatedStatementTrait), namespace.parser_info

            return namespace.parser_info.CreateConcreteTypeFactory(self)

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
