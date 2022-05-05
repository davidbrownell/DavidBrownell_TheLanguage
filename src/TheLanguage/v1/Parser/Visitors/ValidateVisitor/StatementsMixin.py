# ----------------------------------------------------------------------
# |
# |  StatementsMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-27 13:45:48
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

from contextlib import contextmanager

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ...Helpers import MiniLanguageHelpers

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo, IfStatementClauseParserInfo, IfStatementElseClauseParserInfo
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportStatementItemParserInfo
    from ...ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo


# ----------------------------------------------------------------------
class StatementsMixin(BaseMixin):

    # ----------------------------------------------------------------------
    # |  ClassAttributeStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassAttributeStatementParserInfo(
        self,
        parser_info: ClassAttributeStatementParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    # |  ClassStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassStatementParserInfo(
        self,
        parser_info: ClassStatementParserInfo,
    ):
        # Add scope for templates and constraints
        if parser_info.templates or parser_info.constraints:
            pass # TODO: self._compile_time_info.PushScope()

        yield

        # Remove scope for templates and constraints
        if parser_info.templates or parser_info.constraints:
            pass # TODO: self._compile_time_info.PopScope()

    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassStatementDependencyParserInfo(
        self,
        parser_info: ClassStatementDependencyParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    # |  FuncDefinitionStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncDefinitionStatementParserInfo(
        self,
        parser_info: FuncDefinitionStatementParserInfo,
    ):
        # Add scope for templates
        if parser_info.templates:
            pass # TODO: self._compile_time_info.PushScope()

        yield

        # Remove scope for templates
        if parser_info.templates:
            pass # TODO: self._compile_time_info.PopScope()

    # ----------------------------------------------------------------------
    # |  FuncInvocationStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncInvocationStatementParserInfo(
        self,
        parser_info: FuncInvocationStatementParserInfo,
    ):
        parser_info_type = parser_info.parser_info_type__

        if parser_info_type == ParserInfoType.Configuration:
            MiniLanguageHelpers.EvalExpression(parser_info.expression, self._configuration_info)
        elif parser_info_type == ParserInfoType.TypeCustomization:
            pass # Nothing to do here on this pass
        else:
            raise NotImplementedError("TODO")  # TODO

        yield

    # ----------------------------------------------------------------------
    # |  IfStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ):
        parser_info_type = parser_info.parser_info_type__

        if parser_info_type == ParserInfoType.Configuration:
            matched_clause = False

            for clause in parser_info.clauses:
                execute_flag = False

                if not matched_clause:
                    clause_result = MiniLanguageHelpers.EvalExpression(clause.expression, self._configuration_info)
                    clause_result = clause_result.type.ToBoolValue(clause_result.value)

                    if clause_result:
                        execute_flag = True
                        matched_clause = True

                self.__class__._SetExecuteFlag(clause, execute_flag)  # pylint: disable=protected-access

            if parser_info.else_clause:
                self.__class__._SetExecuteFlag(parser_info.else_clause, not matched_clause)  # pylint: disable=protected-access

        elif parser_info_type ==ParserInfoType.TypeCustomization:
            raise NotImplementedError("TODO") # TODO

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementClauseParserInfo(
        self,
        parser_info: IfStatementClauseParserInfo,
    ):
        if not self.__class__._GetExecuteFlag(parser_info):  # pylint: disable=protected-access
            yield VisitResult.SkipAll
        else:
            yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementElseClauseParserInfo(
        self,
        parser_info: IfStatementElseClauseParserInfo,
    ):
        if not self.__class__._GetExecuteFlag(parser_info):  # pylint: disable=protected-access
            yield VisitResult.SkipAll
        else:
            yield

    # ----------------------------------------------------------------------
    # |  ImportStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnImportStatementParserInfo(
        self,
        parser_info: ImportStatementParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    def OnImportStatementItemParserInfo(
        self,
        parser_info: ImportStatementItemParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  PassStatementParserInfo
    # ----------------------------------------------------------------------
    def OnPassStatementParserInfo(
        self,
        parser_info: PassStatementParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  SpecialMethodStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnSpecialMethodStatementParserInfo(
        self,
        parser_info: SpecialMethodStatementParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    # |  TypeAliasStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnTypeAliasStatementParserInfo(
        self,
        parser_info: TypeAliasStatementParserInfo,
    ):
        yield
