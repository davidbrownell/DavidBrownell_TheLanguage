# ----------------------------------------------------------------------
# |
# |  BaseMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:17:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BaseMixin object"""

import itertools
import os
import threading
import types

from contextlib import contextmanager, ExitStack
from enum import auto, Enum
from typing import Callable, cast, Dict, List, Optional, Set, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import CreateError, Error, ErrorException
    from ...TranslationUnitRegion import TranslationUnitRegion
    from ...Common import MiniLanguageHelpers

    from ...ParserInfos.AggregateParserInfo import AggregateParserInfo
    from ...ParserInfos.ParserInfo import ParserInfo, ParserInfoType, VisitResult
    from ...ParserInfos.ParserInfoVisitorHelper import ParserInfoVisitorHelper

    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo
    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier

    from ...ParserInfos.Expressions.BinaryExpressionParserInfo import BinaryExpressionParserInfo, OperatorType as BinaryExpressionOperatorType
    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Expressions.FuncOrTypeExpressionParserInfo import FuncOrTypeExpressionParserInfo
    from ...ParserInfos.Expressions.NestedTypeExpressionParserInfo import NestedTypeExpressionParserInfo
    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo
    from ...ParserInfos.Expressions.TupleExpressionParserInfo import TupleExpressionParserInfo
    from ...ParserInfos.Expressions.TypeCheckExpressionParserInfo import OperatorType as TypeCheckExpressionOperatorType
    from ...ParserInfos.Expressions.VariableExpressionParserInfo import VariableExpressionParserInfo
    from ...ParserInfos.Expressions.VariantExpressionParserInfo import VariantExpressionParserInfo

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ConcreteTypeInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo, ScopeFlag
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo
    from ...ParserInfos.Statements import HierarchyInfo

    from ...ParserInfos.Statements.Traits.ScopedStatementTrait import ScopedStatementTrait
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Traits.NamedTrait import NamedTrait


# ----------------------------------------------------------------------
InvalidTypeError                            = CreateError(
    "'{name}' is not a recognized type",
    name=str,
)

InvalidTypeVisibilityError                  = CreateError(
    "'{name}' is a recognized type, but not visible in this context",
    name=str,
    dependency_enumerations=List[HierarchyInfo.Dependency.EnumResult],
)

InvalidTypeReferenceError                   = CreateError(
    "'{name}' is not a valid type reference; types must be class-like or aliases to class-like types",
    name=str,
)

InvalidCompileTimeTypeCheckError            = CreateError(
    "Compile-time type checks can only be used with template types",
)


# ----------------------------------------------------------------------
class BaseMixin(ParserInfoVisitorHelper):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class ProcessType(Enum):
        ClassesSequential                   = 0
        FuncsAndTypesParallel               = auto()

    # BugBug: Remove this
    class PostprocessType(Enum):
        ResolveDependenciesParallel         = 0
        ResolveDependenciesSequential       = 1
        ResolveNestedClassTypes             = 2
        # BugBug?: ResolveFunctionTypes                = 3

    # BugBug: Remove this
    sequential_postprocess_steps: Set[PostprocessType]  = set(
        [
            PostprocessType.ResolveDependenciesSequential,
        ],
    )

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        configuration_info: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
        fundamental_types_namespace: Optional[NamespaceInfo],
        this_namespace: ParsedNamespaceInfo,
    ):
        namespace_stack: List[NamespaceInfo] = []

        if fundamental_types_namespace is not None:
            namespace_stack.append(fundamental_types_namespace)

        self._errors: List[Error]           = []

        self._all_postprocess_funcs: List[List[Callable[[], None]]]         = [[] for _ in range(len(BaseMixin.PostprocessType))]

        self._namespaces_stack              = [namespace_stack, ]
        self._compile_time_stack            = [configuration_info, ]

        self._root_namespace                = this_namespace

    # ----------------------------------------------------------------------
    @contextmanager
    def OnPhrase(
        self,
        parser_info: ParserInfo,
    ):
        try:
            with ExitStack() as exit_stack:
                if isinstance(parser_info, NamedTrait):
                    assert self._namespaces_stack
                    namespace_stack = self._namespaces_stack[-1]

                    if not isinstance(parser_info, RootStatementParserInfo):
                        assert namespace_stack
                        namespace = namespace_stack[-1]

                        assert isinstance(namespace, ParsedNamespaceInfo), namespace

                        if isinstance(namespace.parser_info, RootStatementParserInfo):
                            scope_flag = ScopeFlag.Root
                        else:
                            assert isinstance(namespace.parent, ParsedNamespaceInfo), namespace.parent
                            scope_flag = namespace.parent.scope_flag

                        if parser_info.IsNameOrdered(scope_flag):
                            ordered_item_or_items = namespace.ordered_children[parser_info.name]

                            for ordered_item in (ordered_item_or_items if isinstance(ordered_item_or_items, list) else [ordered_item_or_items, ]):
                                namespace.AddChild(ordered_item)

                    if isinstance(parser_info, ScopedStatementTrait):
                        if isinstance(parser_info, RootStatementParserInfo):
                            namespace = self._root_namespace
                        else:
                            assert self._namespaces_stack
                            namespace_stack = self._namespaces_stack[-1]

                            assert namespace_stack
                            namespace = namespace_stack[-1]

                            namespace = namespace.children[parser_info.name]

                            if isinstance(namespace, list):
                                for potential_namespace in namespace:
                                    if potential_namespace.parser_info is parser_info:
                                        namespace = potential_namespace
                                        break

                        assert isinstance(namespace, NamespaceInfo)

                        assert self._namespaces_stack
                        namespace_stack = self._namespaces_stack[-1]

                        namespace_stack.append(namespace)
                        exit_stack.callback(namespace_stack.pop)

                # BugBug assert self._compile_time_stack
                # BugBug with parser_info.InitTypeCustomization(
                # BugBug     self._compile_time_stack[-1],
                # BugBug ) as visit_result:
                # BugBug     yield visit_result
                # BugBug
                # BugBug return # BugBug
                # BugBug
                # BugBug # BugBug:
                # BugBug
                # BugBug is_type_expression = False
                # BugBug is_compile_time_expression = False
                # BugBug
                # BugBug if isinstance(parser_info, ExpressionParserInfo):
                # BugBug     if parser_info.IsType() is not False:
                # BugBug         is_type_expression = True
                # BugBug
                # BugBug         # ----------------------------------------------------------------------
                # BugBug         def TypeCheckCallback(
                # BugBug             the_type: str,
                # BugBug             operator: TypeCheckExpressionOperatorType,
                # BugBug             dest_parser_info: ExpressionParserInfo,
                # BugBug         ) -> bool:
                # BugBug             # TODO: It is no longer valid to just throw, as we are looking at templated types
                # BugBug             raise ErrorException(
                # BugBug                 InvalidCompileTimeTypeCheckError.Create(
                # BugBug                     region=dest_parser_info.regions__.self__,
                # BugBug                 ),
                # BugBug             )
                # BugBug
                # BugBug         # ----------------------------------------------------------------------
                # BugBug
                # BugBug         try:
                # BugBug             type_result = MiniLanguageHelpers.EvalType(
                # BugBug                 parser_info,
                # BugBug                 self._compile_time_stack,
                # BugBug                 TypeCheckCallback,
                # BugBug             )
                # BugBug
                # BugBug             if isinstance(type_result, MiniLanguageHelpers.MiniLanguageType):
                # BugBug                 parser_info.SetResolvedEntity(type_result)
                # BugBug
                # BugBug             elif isinstance(type_result, ExpressionParserInfo):
                # BugBug                 try:
                # BugBug                     self._ResolveType(
                # BugBug                         parser_info,
                # BugBug                         type_result,
                # BugBug                         self._NamespaceTypeResolver,
                # BugBug                     )
                # BugBug                 except ErrorException:
                # BugBug                     # It is possible that we see this error right now because we
                # BugBug                     # are in a class and the type is defined in a base. Wait until
                # BugBug                     # the class is fully defined (so the base types are visible)
                # BugBug                     # and attempt to get the type again.
                # BugBug
                # BugBug                     suppress_exception = False
                # BugBug
                # BugBug                     assert self._namespaces_stack
                # BugBug                     namespace_stack = self._namespaces_stack[-1]
                # BugBug
                # BugBug                     assert namespace_stack
                # BugBug
                # BugBug                     for namespace_index, namespace in enumerate(reversed(namespace_stack)):
                # BugBug                         # Don't look at the initial (or last since the list is being reversed)
                # BugBug                         # namespace, as that will either be the class or a type nested in the class.
                # BugBug                         # If it is the class, we are in the process of resolving its dependencies and
                # BugBug                         # want to see unrecognized types as errors. If it is something within the class,
                # BugBug                         # it won't resolve the type and is safe to skip.
                # BugBug                         if namespace_index == 0:
                # BugBug                             continue
                # BugBug
                # BugBug                         if (
                # BugBug                             isinstance(namespace, ParsedNamespaceInfo)
                # BugBug                             and isinstance(namespace.parser_info, ClassStatementParserInfo)
                # BugBug                             and any(
                # BugBug                                 not dependency.is_disabled__
                # BugBug                                 for dependency in itertools.chain(
                # BugBug                                     (namespace.parser_info.extends or []),
                # BugBug                                     (namespace.parser_info.uses or []),
                # BugBug                                     (namespace.parser_info.implements or []),
                # BugBug                                 )
                # BugBug                             )
                # BugBug                         ):
                # BugBug                             suppress_exception = True
                # BugBug
                # BugBug                             # Process it once the classes have been fully formed
                # BugBug                             if namespace.parser_info.default_initializable:
                # BugBug                                 # ----------------------------------------------------------------------
                # BugBug                                 def ResolveNestedType(
                # BugBug                                     parser_info=parser_info,
                # BugBug                                     type_result=type_result,
                # BugBug                                     namespace=namespace,
                # BugBug                                 ):
                # BugBug                                     return # BugBug: Not yet
                # BugBug
                # BugBug                                     self._ResolveType(
                # BugBug                                         parser_info,
                # BugBug                                         type_result,
                # BugBug                                         (
                # BugBug                                             lambda
                # BugBug                                                 type_name,
                # BugBug                                                 region,
                # BugBug                                                 namespace=namespace,
                # BugBug                                             :
                # BugBug                                                 self.__class__._NestedTypeResolver(  # pylint: disable=protected-access
                # BugBug                                                     type_name,
                # BugBug                                                     region,
                # BugBug                                                     namespace.parser_info.GetOrCreateConcreteTypeInfo(None),
                # BugBug                                                 )
                # BugBug                                         )
                # BugBug                                     )
                # BugBug
                # BugBug                                 # ----------------------------------------------------------------------
                # BugBug
                # BugBug                                 self._all_postprocess_funcs[BaseMixin.PostprocessType.ResolveNestedClassTypes.value].append(ResolveNestedType)
                # BugBug
                # BugBug                             break
                # BugBug
                # BugBug                     if not suppress_exception:
                # BugBug                         raise
                # BugBug
                # BugBug             else:
                # BugBug                 assert False, type_result  # pragma: no cover
                # BugBug
                # BugBug         except ErrorException as ex:
                # BugBug             self._errors += ex.errors
                # BugBug
                # BugBug         yield VisitResult.SkipAll
                # BugBug         return
                # BugBug
                # BugBug     elif parser_info.is_compile_time__:
                # BugBug         is_compile_time_expression = True
                # BugBug
                # BugBug with parser_info.InitTypeCustomization():
                # BugBug     yield
                # BugBug
                # BugBug assert not is_type_expression or id(parser_info) in self._processed, (
                # BugBug     "Internal Error",
                # BugBug     parser_info.__class__.__name__,
                # BugBug )
                # BugBug
                # BugBug # TODO: assert (
                # BugBug # TODO:     not is_compile_time_expression
                # BugBug # TODO:     or cast(ExpressionParserInfo, parser_info).HasResolvedEntity()
                # BugBug # TODO: ), (
                # BugBug # TODO:     "Internal Error",
                # BugBug # TODO:     parser_info.__class__.__name__,
                # BugBug # TODO: )

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    def _ResolveType(
        self,
        parser_info: ExpressionParserInfo,
        type_result: ExpressionParserInfo,
        resolver_func: Callable[
            [
                str,
                TranslationUnitRegion,
            ],
            Optional[
                Tuple[
                    VisibilityModifier,
                    Union[
                        ClassStatementParserInfo,
                        TemplateTypeParameterParserInfo,
                        TypeAliasStatementParserInfo,
                    ],
                    bool,                   # is_class
                ]
            ],
        ],
    ) -> None:
        if parser_info.HasResolvedEntity():
            return

        resolved_type: Optional[ExpressionParserInfo.ResolvedType] = None

        if isinstance(type_result, FuncOrTypeExpressionParserInfo):
            assert isinstance(type_result.value, str), type_result.value

            resolved_parser_info = resolver_func(type_result.value, type_result.regions__.self__)
            if resolved_parser_info is None:
                raise ErrorException(
                    InvalidTypeError.Create(
                        region=type_result.regions__.value,
                        name=type_result.value,
                    ),
                )

            resolved_visibility, resolved_parser_info, is_class_member = resolved_parser_info

            if not isinstance(
                resolved_parser_info,
                (
                    ClassStatementParserInfo,
                    TemplateTypeParameterParserInfo,
                    TypeAliasStatementParserInfo,
                ),
            ):
                raise ErrorException(
                    InvalidTypeReferenceError.Create(
                        region=type_result.regions__.value,
                        name=type_result.value,
                    ),
                )

            if isinstance(resolved_parser_info, TypeAliasStatementParserInfo):
                resolved_type = TypeAliasStatementParserInfo.ResolvedType.Create(
                    resolved_visibility,
                    resolved_parser_info,
                    is_class_member,
                )
            else:
                resolved_type = ExpressionParserInfo.ResolvedType.Create(
                    resolved_visibility,
                    resolved_parser_info,
                    is_class_member,
                )

        elif isinstance(type_result, NestedTypeExpressionParserInfo):
            raise NotImplementedError("TODO: Not implemented yet")

        elif isinstance(type_result, NoneExpressionParserInfo):
            parser_info.SetResolvedEntity(None)
            return

        elif isinstance(type_result, (TupleExpressionParserInfo, VariantExpressionParserInfo)):
            errors: List[Error] = []

            for the_type in type_result.types:
                try:
                    self._ResolveType(the_type, the_type, resolver_func)
                except ErrorException as ex:
                    errors += ex.errors

            if errors:
                raise ErrorException(*errors)

            # BugBug: Type visibility needs to be based on child types

            resolved_type = ExpressionParserInfo.ResolvedType.Create(
                VisibilityModifier.public,
                VisibilityModifier.public,
                type_result,
            )

        assert resolved_type is not None
        parser_info.SetResolvedEntity(resolved_type)

    # ----------------------------------------------------------------------
    def _NamespaceTypeResolver(
        self,
        type_name: str,
        region: TranslationUnitRegion,
    ) -> Optional[
        Tuple[
            VisibilityModifier,
            Union[
                ClassStatementParserInfo,
                TemplateTypeParameterParserInfo,
                TypeAliasStatementParserInfo,
            ],
            bool,
        ]
    ]:
        assert self._namespaces_stack
        namespace_stack = self._namespaces_stack[-1]

        assert namespace_stack

        for namespace in reversed(namespace_stack):
            potential_namespace = namespace.children.get(type_name, None)
            if potential_namespace is not None:
                assert isinstance(potential_namespace, ParsedNamespaceInfo), potential_namespace

                assert isinstance(
                    potential_namespace.parser_info,
                    (
                        ClassStatementParserInfo,
                        TemplateTypeParameterParserInfo,
                        TypeAliasStatementParserInfo,
                    ),
                ), potential_namespace.parser_info

                return (
                    VisibilityModifier.public,
                    potential_namespace.parser_info,
                    False,
                )

        return None

    # ----------------------------------------------------------------------
    @staticmethod
    def _NestedTypeResolver(
        type_name: str,
        region: TranslationUnitRegion,
        concrete_type_info: ConcreteTypeInfo,
    ) -> Optional[
        Tuple[
            VisibilityModifier,
            Union[
                ClassStatementParserInfo,
                TemplateTypeParameterParserInfo,
                TypeAliasStatementParserInfo,
            ],
            bool,
        ]
    ]:
        for dependency in concrete_type_info.types.Enum():
            hierarchy_info = dependency.ResolveHierarchy()

            if hierarchy_info.statement.name == type_name:
                if hierarchy_info.visibility is None:
                    raise ErrorException(
                        InvalidTypeVisibilityError.Create(
                            region=region,
                            name=type_name,
                            dependency_enumerations=list(dependency.EnumHierarchy()),
                        ),
                    )

                assert isinstance(
                    hierarchy_info.statement,
                    (
                        ClassStatementParserInfo,
                        TemplateTypeParameterParserInfo,
                        TypeAliasStatementParserInfo,
                    ),
                ), hierarchy_info.statement

                return (
                    hierarchy_info.visibility,
                    hierarchy_info.statement,
                    True,
                )

        return None
