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
    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import CreateError, Error, ErrorException
    from ...TranslationUnitRegion import TranslationUnitRegion

    from ...ParserInfos.ParserInfo import ParserInfo, ParserInfoType, VisitResult
    from ...ParserInfos.AggregateParserInfo import AggregateParserInfo

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

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo, ScopeFlag
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...ParserInfos.Statements.Traits.NamedStatementTrait import NamedStatementTrait
    from ...ParserInfos.Statements.Traits.ScopedStatementTrait import ScopedStatementTrait
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait


# ----------------------------------------------------------------------
InvalidTypeError                            = CreateError(
    "'{name}' is not a recognized type",
    name=str,
)

InvalidTypeReferenceError                   = CreateError(
    "'{name}' is not a valid type reference; types must be class-like or aliases to class-like types",
    name=str,
)

InvalidCompileTimeTypeCheckError            = CreateError(
    "Compile-time type checks can only be used with template types",
)


# ----------------------------------------------------------------------
class BaseMixin(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class PostprocessType(Enum):
        ResolveIso                          = 0
        ResolveDependenciesParallel         = 1
        ResolveDependenciesSequential       = 2
        ResolveClasses                      = 3
        ResolveNestedTypes                  = 4

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

        self._namespaces_stack              = [namespace_stack, ]
        self._compile_time_stack            = [configuration_info, ]

        self._root_namespace                = this_namespace

        self._errors: List[Error]           = []
        self._processed: Set[int]           = set()

        self._all_postprocess_funcs: List[List[Callable[[], None]]]         = [[] for _ in range(len(BaseMixin.PostprocessType))]

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        # TODO: Use ParserInfoVisitorHelper

        index = name.find("ParserInfo__")
        if index != -1 and index + len("ParserInfo__") + 1 < len(name):
            return types.MethodType(self.__class__._DefaultDetailMethod, self)  # pylint: disable=protected-access

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    @contextmanager
    def OnPhrase(
        self,
        parser_info: ParserInfo,
    ):
        try:
            with ExitStack() as exit_stack:
                if isinstance(parser_info, NamedStatementTrait):
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

                is_type_expression = False
                is_compile_time_expression = False

                if isinstance(parser_info, ExpressionParserInfo):
                    if parser_info.IsType() is not False:
                        is_type_expression = True

                        # ----------------------------------------------------------------------
                        def TypeCheckCallback(
                            the_type: str,
                            operator: TypeCheckExpressionOperatorType,
                            dest_parser_info: ExpressionParserInfo,
                        ) -> bool:
                            # TODO: It is no longer valid to just throw, as we are looking at templated types
                            raise ErrorException(
                                InvalidCompileTimeTypeCheckError.Create(
                                    region=dest_parser_info.regions__.self__,
                                ),
                            )

                        # ----------------------------------------------------------------------

                        try:
                            type_result = MiniLanguageHelpers.EvalType(
                                parser_info,
                                self._compile_time_stack,
                                TypeCheckCallback,
                            )

                            if isinstance(type_result, MiniLanguageHelpers.MiniLanguageType):
                                parser_info.SetResolvedEntity(type_result)

                            elif isinstance(type_result, ExpressionParserInfo):
                                try:
                                    self._ResolveType(
                                        parser_info,
                                        type_result,
                                        self._NamespaceTypeResolver,
                                    )
                                except ErrorException:
                                    # It is possible that we see this error right now because we
                                    # are in a class and the type is defined in a base. Wait until
                                    # the class is fully defined (so the base types are visible)
                                    # and attempt to get the type again.

                                    suppress_exception = False

                                    assert self._namespaces_stack
                                    namespace_stack = self._namespaces_stack[-1]

                                    assert namespace_stack

                                    for namespace in reversed(namespace_stack):
                                        if (
                                            isinstance(namespace, ParsedNamespaceInfo)
                                            and isinstance(namespace.parser_info, ClassStatementParserInfo)
                                            and any(
                                                not dependency.is_disabled__
                                                for dependency in itertools.chain(
                                                    (namespace.parser_info.extends or []),
                                                    (namespace.parser_info.uses or []),
                                                    (namespace.parser_info.implements or []),
                                                )
                                            )
                                        ):
                                            # Process it once the classes have been fully formed
                                            suppress_exception = True

                                            # ----------------------------------------------------------------------
                                            def ResolveNestedType(
                                                parser_info=parser_info,
                                                type_result=type_result,
                                                namespace=namespace,
                                            ):
                                                self._ResolveType(
                                                    parser_info,
                                                    type_result,
                                                    (
                                                        lambda type_name, namespace=namespace:
                                                            self._NestedTypeResolver(
                                                                type_name,
                                                                namespace.parser_info,
                                                            )
                                                    )
                                                )

                                            # ----------------------------------------------------------------------

                                            self._all_postprocess_funcs[BaseMixin.PostprocessType.ResolveNestedTypes.value].append(ResolveNestedType)
                                            break

                                    if not suppress_exception:
                                        raise

                            else:
                                assert False, type_result  # pragma: no cover

                        except ErrorException as ex:
                            self._errors += ex.errors

                        yield VisitResult.SkipAll
                        return

                    elif parser_info.is_compile_time__:
                        is_compile_time_expression = True

                yield

                assert not is_type_expression or id(parser_info) in self._processed, (
                    "Internal Error",
                    parser_info.__class__.__name__,
                )

                # TODO: assert (
                # TODO:     not is_compile_time_expression
                # TODO:     or cast(ExpressionParserInfo, parser_info).HasResolvedEntity()
                # TODO: ), (
                # TODO:     "Internal Error",
                # TODO:     parser_info.__class__.__name__,
                # TODO: )

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnRootStatementParserInfo(*args, **kwargs):  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnAggregateParserInfo(*args, **kwargs):  # pylint: disable=unused-argument
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    def _ResolveType(
        self,
        parser_info: ExpressionParserInfo,
        type_result: ExpressionParserInfo,
        resolver_func: Callable[[str], Optional[ParserInfo]],
    ) -> None:
        resolved_type: Optional[ExpressionParserInfo.ResolvedType] = None

        if isinstance(type_result, FuncOrTypeExpressionParserInfo):
            assert isinstance(type_result.value, str), type_result.value

            resolved_parser_info = resolver_func(type_result.value)
            if resolved_parser_info is None:
                raise ErrorException(
                    InvalidTypeError.Create(
                        region=type_result.regions__.value,
                        name=type_result.value,
                    ),
                )

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
                resolved_type = TypeAliasStatementParserInfo.ResolvedType.Create(resolved_parser_info)
            else:
                resolved_type = ExpressionParserInfo.ResolvedType.Create(resolved_parser_info)

        elif isinstance(type_result, NestedTypeExpressionParserInfo):
            raise NotImplementedError("TODO: Not implemented yet")

        elif isinstance(type_result, NoneExpressionParserInfo):
            parser_info.SetResolvedEntity(None)
            return

        elif isinstance(type_result, TupleExpressionParserInfo):
            for the_type in type_result.types:
                self._ResolveType(the_type, the_type, resolver_func)

            resolved_type = ExpressionParserInfo.ResolvedType.Create(type_result)

        elif isinstance(type_result, VariantExpressionParserInfo):
            for the_type in type_result.types:
                self._ResolveType(the_type, the_type, resolver_func)

            resolved_type = ExpressionParserInfo.ResolvedType.Create(type_result)

        assert resolved_type is not None
        parser_info.SetResolvedEntity(resolved_type)

    # ----------------------------------------------------------------------
    def _NamespaceTypeResolver(
        self,
        type_name: str,
    ) -> Optional[ParserInfo]:
        assert self._namespaces_stack
        namespace_stack = self._namespaces_stack[-1]

        assert namespace_stack

        for namespace in reversed(namespace_stack):
            potential_namespace = namespace.children.get(type_name, None)
            if potential_namespace is not None:
                assert isinstance(potential_namespace, ParsedNamespaceInfo), potential_namespace
                return potential_namespace.parser_info

        return None

    # ----------------------------------------------------------------------
    def _NestedTypeResolver(
        self,
        type_name: str,
        class_parser_info: ClassStatementParserInfo,
    ) -> Optional[ParserInfo]:
        assert False, "BugBug"
        pass # BugBug
        return None

    # ----------------------------------------------------------------------
    def _DefaultDetailMethod(
        self,
        parser_info_or_infos: Union[ParserInfo, List[ParserInfo]],
        *,
        include_disabled: bool,
    ):
        if isinstance(parser_info_or_infos, list):
            for parser_info in parser_info_or_infos:
                parser_info.Accept(
                    self,
                    include_disabled=include_disabled,
                )
        else:
            parser_info_or_infos.Accept(
                self,
                include_disabled=include_disabled,
            )
