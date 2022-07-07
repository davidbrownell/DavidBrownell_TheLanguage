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
    from ...ParserInfos.ParserInfo import CompileTimeInfo, ParserInfo, ParserInfoType, VisitResult
    from ...ParserInfos.ParserInfoVisitorHelper import ParserInfoVisitorHelper

    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateDecoratorParameterParserInfo, TemplateTypeParameterParserInfo
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

    from ...ParserInfos.Expressions.Traits.SimpleExpressionTrait import SimpleExpressionTrait

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo, ScopeFlag
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo
    # BugBug from ...ParserInfos.Statements import HierarchyInfo

    from ...ParserInfos.Statements.Traits.ScopedStatementTrait import ScopedStatementTrait
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Traits.NamedTrait import NamedTrait


# ----------------------------------------------------------------------

# BugBug InvalidTypeVisibilityError                  = CreateError(
# BugBug     "'{name}' is a recognized type, but not visible in this context",
# BugBug     name=str,
# BugBug     dependency_enumerations=List[HierarchyInfo.Dependency.EnumResult],
# BugBug )

InvalidTypeReferenceError                   = CreateError(
    "'{name}' is not a valid type reference; types must be class-like or aliases to class-like types",
    name=str,
)

InvalidCompileTimeTypeCheckError            = CreateError(
    "Compile-time type checks can only be used with template types",
)


InvalidMiniLanguageEvalResultError          = CreateError(
    "A compile-time expression was expected",
)

InvalidTypeError                            = CreateError(
    "A standard type was expected",
)

InvalidExpressionError                      = CreateError(
    "A standard expression was expected",
)


# ----------------------------------------------------------------------
class BaseMixin(ParserInfoVisitorHelper):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class ProcessType(Enum):
        ClassesParallel                     = 0
        AllTypesParallel                    = auto()

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
        configuration_info: Dict[str, CompileTimeInfo],
        fundamental_types_namespace: Optional[NamespaceInfo],
        this_namespace: ParsedNamespaceInfo,
    ):
        namespace_stack: List[NamespaceInfo] = []

        if fundamental_types_namespace is not None:
            namespace_stack.append(fundamental_types_namespace)

        self._errors: List[Error]           = []

        self._all_postprocess_funcs: List[List[Callable[[], None]]]         = [[] for _ in range(len(BaseMixin.PostprocessType))]

        self._namespaces_stack                                              = [namespace_stack, ]
        self._compile_time_stack                                            = [configuration_info, ]

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

                yield

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
    @staticmethod
    def _NestedTypeResolver(
        type_name: str,
        region: TranslationUnitRegion,
        concrete_type_info, # BugBug : ConcreteTypeInfo,
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
