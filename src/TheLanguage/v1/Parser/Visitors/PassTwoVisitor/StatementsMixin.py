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

    from ...ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo
    from ...ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo
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
    @staticmethod
    @contextmanager
    def OnClassStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnClassStatementDependencyParserInfo(*args, **kwargs):
        # BugBug: Validate is single type
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
        if parser_info.parser_info_type__ == ParserInfoType.TypeCustomization:
            MiniLanguageHelpers.EvalExpression(
                parser_info.expression,
                [self._configuration_info], # BugBug: Is this right?
                self._namespaces_stack[-1],
            )

        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnIfStatementParserInfo(*args, **kwargs):
        # BugBug: Do this
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
    def OnImportStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnPassStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnSpecialMethodStatementParserInfo(
        self,
        parser_info: SpecialMethodStatementParserInfo,
    ):
        assert self._namespaces_stack
        namespace_stack = self._namespaces_stack[-1]

        assert namespace_stack
        namespace = namespace_stack[-1]

        assert namespace.parent
        parent_namespace = namespace.parent

        assert isinstance(parent_namespace, ParsedNamespaceInfo), parent_namespace
        assert isinstance(parent_namespace.parser_info, ClassStatementParserInfo), parent_namespace.parser_info

        class_statement_parser_info = parent_namespace.parser_info

        with ExitStack() as exit_stack:
            if parser_info.special_method_type == SpecialMethodType.CompileTimeEvalConstraints:
                # Add all of the constraints
                BugBug = 10


        # BugBug: Add constraints to stack

            assert parser_info.parser_info_type__ == ParserInfoType.TypeCustomization, parser_info.parser_info_type__
            parser_info.SetValidatedFlag()

            yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTypeAliasStatementParserInfo(*args, **kwargs):
        yield
