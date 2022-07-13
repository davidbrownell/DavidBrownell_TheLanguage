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

    from ..Namespaces import ParsedNamespace, VisibilityModifier

    from ...Common import MiniLanguageHelpers
    from ...Error import CreateError, ErrorException

    from ...ParserInfos.Expressions.NoneExpressionParserInfo import NoneExpressionParserInfo

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo, SpecialMethodType
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo


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
        if parser_info.templates is None or parser_info.templates.is_default_initializable:
            self.CreateConcreteType(parser_info, None)

            yield VisitResult.SkipAll
            return

        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnClassStatementDependencyParserInfo_(*args, **kwargs):
        yield

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
    @contextmanager
    def OnSpecialMethodStatementParserInfo(
        self,
        parser_info: SpecialMethodStatementParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTypeAliasStatementParserInfo(
        self,
        parser_info: TypeAliasStatementParserInfo,
    ):
        if parser_info.templates is None or parser_info.templates.is_default_initializable:
            self.CreateConcreteType(parser_info, None)

            yield VisitResult.SkipAll
            return

        yield
