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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ...ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo, IfStatementClauseParserInfo
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportStatementItemParserInfo
    from ...ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo


# ----------------------------------------------------------------------
class StatementsMixin(BaseMixin):

    # ----------------------------------------------------------------------
    # |  ClassAttributeStatementParserInfo
    # ----------------------------------------------------------------------
    def OnClassAttributeStatementParserInfo(
        self,
        parser_info: ClassAttributeStatementParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  ClassStatementParserInfo
    # ----------------------------------------------------------------------
    def OnEnterClassStatementParserInfo(
        self,
        parser_info: ClassStatementParserInfo,
    ):
        # Add scope for templates and constraints
        if parser_info.templates or parser_info.constraints:
            self._compile_time_info.PushScope()

    # ----------------------------------------------------------------------
    def OnExitClassStatementParserInfo(
        self,
        parser_info: ClassStatementParserInfo,
    ):
        # Remove scope for templates and constraints
        if parser_info.templates or parser_info.constraints:
            self._compile_time_info.PopScope()

    # ----------------------------------------------------------------------
    def OnClassStatementDependencyParserInfo(
        self,
        parser_info: ClassStatementDependencyParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  FuncDefinitionStatementParserInfo
    # ----------------------------------------------------------------------
    def OnEnterFuncDefinitionStatementParserInfo(
        self,
        parser_info: FuncDefinitionStatementParserInfo,
    ):
        # Add scope for templates
        if parser_info.templates:
            self._compile_time_info.PushScope()

    # ----------------------------------------------------------------------
    def OnExitFuncDefinitionStatementParserInfo(
        self,
        parser_info: FuncDefinitionStatementParserInfo,
    ):
        # Remove scope for templates
        if parser_info.templates:
            self._compile_time_info.PopScope()

    # ----------------------------------------------------------------------
    # |  IfStatementParserInfo
    # ----------------------------------------------------------------------
    def OnIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    def OnIfStatementClauseParserInfo(
        self,
        parser_info: IfStatementClauseParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  ImportStatementParserInfo
    # ----------------------------------------------------------------------
    def OnImportStatementParserInfo(
        self,
        parser_info: ImportStatementParserInfo,
    ):
        pass

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
    def OnSpecialMethodStatementParserInfo(
        self,
        parser_info: SpecialMethodStatementParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  TypeAliasStatementParserInfo
    # ----------------------------------------------------------------------
    def OnEnterTypeAliasStatementParserInfo(
        self,
        parser_info: TypeAliasStatementParserInfo,
    ):
        # Add scope for templates or constraints
        if parser_info.templates or parser_info.constraints:
            self._compile_time_info.PushScope()

    # ----------------------------------------------------------------------
    def OnExitTypeAliasStatementParserInfo(
        self,
        parser_info: TypeAliasStatementParserInfo,
    ):
        # Remove scope for templates or constraints
        if parser_info.templates or parser_info.constraints:
            self._compile_time_info.PopScope()
