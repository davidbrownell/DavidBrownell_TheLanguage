# ----------------------------------------------------------------------
# |
# |  StatementsMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:17:58
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StatementsMixin object"""

import os

from contextlib import contextmanager, ExitStack
from typing import Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import ParsedNamespaceInfo, ScopeFlag, VisibilityModifier

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...Error import CreateError, ErrorException

    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo

    from ...ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo


# ----------------------------------------------------------------------
InvalidClassDependencyError                 = CreateError(
    "Invalid class dependency",
)


# ----------------------------------------------------------------------
class StatementsMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnClassAttributeStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassStatementParserInfo(
        self,
        parser_info: ClassStatementParserInfo,
    ):
        yield

        # ----------------------------------------------------------------------
        def ResolveDependenciesParallelCallback():
            parser_info.class_capabilities.ValidateDependencies(parser_info)

        # ----------------------------------------------------------------------
        def ResolveDependenciesSequentialCallback():
            parser_info.Initialize()

        # ----------------------------------------------------------------------
        def ResolveClassCallback():
            # BugBug
            pass

        # ----------------------------------------------------------------------

        self._all_postprocess_funcs[BaseMixin.PostprocessType.ResolveDependenciesParallel.value].append(ResolveDependenciesParallelCallback)
        self._all_postprocess_funcs[BaseMixin.PostprocessType.ResolveDependenciesSequential.value].append(ResolveDependenciesSequentialCallback)
        self._all_postprocess_funcs[BaseMixin.PostprocessType.ResolveClasses.value].append(ResolveClassCallback)

    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassStatementDependencyParserInfo(
        self,
        parser_info: ClassStatementDependencyParserInfo,
    ):
        yield

        # Defer verifying that the dependency is a valid type, as we might be
        # accessing an alias that has not yet been defined (and therefore is
        # not resolved).

        # ----------------------------------------------------------------------
        def Callback():
            if parser_info.type.ResolvedEntityIsNone():
                parser_info.Disable()
                return

            resolved_type = parser_info.type.resolved_type__.Resolve()

            if not isinstance(resolved_type.parser_info, ClassStatementParserInfo):
                raise ErrorException(
                    InvalidClassDependencyError.Create(
                        region=resolved_type.parser_info.regions__.self__,
                    ),
                )

        # ----------------------------------------------------------------------

        self._all_postprocess_funcs[BaseMixin.PostprocessType.ResolveIso.value].append(Callback)

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnFuncDefinitionStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncInvocationStatementParserInfo(
        self,
        parser_info: FuncInvocationStatementParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnIfStatementClauseParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnIfStatementElseClauseParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnImportStatementParserInfo(
        parser_info: ImportStatementParserInfo,
    ):
        yield

        # Now that all namespace processing has been completed, we can safely
        # disable this statement so that it doesn't import other processing.
        parser_info.Disable()

    # ----------------------------------------------------------------------
    @contextmanager
    def OnSpecialMethodStatementParserInfo(
        self,
        parser_info: SpecialMethodStatementParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTypeAliasStatementParserInfo(*args, **kwargs):
        yield
