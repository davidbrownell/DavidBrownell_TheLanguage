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

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Namespaces import Namespace, ParsedNamespace

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

    from ...ParserInfos.Statements.ConcreteInfo.ConcreteClass import ConcreteClass

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
        fundamental_types_namespace: Optional[Namespace],
    ):
        self._configuration_info                        = configuration_info
        self._fundamental_types_namespace               = fundamental_types_namespace

        self._context_stack: List[BaseMixin._Context]   = []

        self._errors: List[Error]           = []

        self._all_postprocess_funcs: List[List[Callable[[], None]]]         = [[] for _ in range(len(BaseMixin.PostprocessType))]

    # ----------------------------------------------------------------------
    @contextmanager
    def OnPhrase(
        self,
        parser_info: ParserInfo,
    ):
        try:
            if isinstance(parser_info, RootStatementParserInfo):
                assert not self._context_stack
                self._context_stack.append(
                    self.__class__._Context(
                        parser_info,
                        [self._configuration_info],
                    ),
                )

            assert self._context_stack

            yield

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    # |
    # |  Protected Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class _Context(object):
        # ----------------------------------------------------------------------
        parser_info: ParserInfo
        compile_time_info: List[Dict[str, CompileTimeInfo]]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert isinstance(self.parser_info, NamedTrait), self.parser_info

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    # BugBug @staticmethod
    # BugBug def _NestedTypeResolver(
    # BugBug     type_name: str,
    # BugBug     region: TranslationUnitRegion,
    # BugBug     concrete_type_info, # BugBug : ConcreteTypeInfo,
    # BugBug ) -> Optional[
    # BugBug     Tuple[
    # BugBug         VisibilityModifier,
    # BugBug         Union[
    # BugBug             ClassStatementParserInfo,
    # BugBug             TemplateTypeParameterParserInfo,
    # BugBug             TypeAliasStatementParserInfo,
    # BugBug         ],
    # BugBug         bool,
    # BugBug     ]
    # BugBug ]:
    # BugBug     for dependency in concrete_type_info.types.Enum():
    # BugBug         hierarchy_info = dependency.ResolveHierarchy()
    # BugBug
    # BugBug         if hierarchy_info.statement.name == type_name:
    # BugBug             if hierarchy_info.visibility is None:
    # BugBug                 raise ErrorException(
    # BugBug                     InvalidTypeVisibilityError.Create(
    # BugBug                         region=region,
    # BugBug                         name=type_name,
    # BugBug                         dependency_enumerations=list(dependency.EnumHierarchy()),
    # BugBug                     ),
    # BugBug                 )
    # BugBug
    # BugBug             assert isinstance(
    # BugBug                 hierarchy_info.statement,
    # BugBug                 (
    # BugBug                     ClassStatementParserInfo,
    # BugBug                     TemplateTypeParameterParserInfo,
    # BugBug                     TypeAliasStatementParserInfo,
    # BugBug                 ),
    # BugBug             ), hierarchy_info.statement
    # BugBug
    # BugBug             return (
    # BugBug                 hierarchy_info.visibility,
    # BugBug                 hierarchy_info.statement,
    # BugBug                 True,
    # BugBug             )
    # BugBug
    # BugBug     return None
