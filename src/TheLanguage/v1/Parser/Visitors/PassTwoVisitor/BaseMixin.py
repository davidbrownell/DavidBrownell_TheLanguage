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
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo, ScopeFlag
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo

    from ...ParserInfos.Statements.ConcreteClass import ConcreteClass

    from ...ParserInfos.Statements.Traits.ScopedStatementTrait import ScopedStatementTrait
    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait

    from ...ParserInfos.Traits.NamedTrait import NamedTrait


# ----------------------------------------------------------------------
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
    class PostprocessType(Enum):
        FinalizeConcreteTypes               = 0
        ValidateDefaultConcreteTypes        = auto()
        MethodResolution                    = auto()

    sequential_postprocess_steps: Set[PostprocessType]  = set(
        [],
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
        self._compile_time_info                         = [configuration_info, ]
        self._fundamental_types_namespace               = fundamental_types_namespace

        self._is_initial_pass               = True

        self._root_statement_parser_info: Optional[RootStatementParserInfo] = None

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
                assert self._root_statement_parser_info is None
                self._root_statement_parser_info = parser_info

            if isinstance(parser_info, TemplatedStatementTrait):
                try:
                    concrete_factory = self.CreateConcreteTypeFactory(parser_info)
                    # BugBug: What do we do with the factory?

                except ErrorException as ex:
                    self._errors += ex.errors

                yield VisitResult.SkipAll
                return

            yield

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise
