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

from typing import cast, List, Optional, Union

from contextlib import contextmanager

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ...Error import CreateError
    from ...Helpers import MiniLanguageHelpers
    from ...NamespaceInfo import NamespaceInfo

    from ...ParserInfos.ParserInfo import ParserInfo, ParserInfoType, VisitResult

    from ...ParserInfos.Statements.ClassAttributeStatementParserInfo import ClassAttributeStatementParserInfo
    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo, ClassStatementDependencyParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo, IfStatementClauseParserInfo, IfStatementElseClauseParserInfo
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportStatementItemParserInfo
    from ...ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import ScopeFlag
    from ...ParserInfos.Statements.TypeAliasStatementParserInfo import TypeAliasStatementParserInfo


# ----------------------------------------------------------------------
InvalidIfStatementScopeError                = CreateError(
    "If statements without compile-time expressions are not valid at this level",
)


# ----------------------------------------------------------------------
class StatementsMixin(BaseMixin):

    # TODO: Which of these can we simplify? (via "*args, **kwargs):")

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

        if parser_info_type != ParserInfoType.Configuration:
            # Ensure that other if statements are only used where they are allowed
            parent_scope_flag = self._GetParentScopeFlag()

            if (
                (parser_info_type == ParserInfoType.TypeCustomization and parent_scope_flag == ScopeFlag.Root)
                or (parser_info_type == ParserInfoType.Standard and parent_scope_flag != ScopeFlag.Function)
            ):
                self._errors.append(
                    InvalidIfStatementScopeError.Create(
                        region=parser_info.clauses[0].expression.regions__.self__
                    ),
                )
        else:
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

        yield

        if parser_info_type == ParserInfoType.Configuration:
            # Move everything from the if clause to the proper namespace
            assert isinstance(self._namespace_infos[-1], NamespaceInfo)
            assert None in self._namespace_infos[-1].children
            assert isinstance(self._namespace_infos[-1].children[None], list)

            namespace_items = cast(List[Union[NamespaceInfo, ParserInfo]], self._namespace_infos[-1].children[None])
            assert len(namespace_items) >= 2
            assert isinstance(namespace_items[-2], IfStatementParserInfo)
            assert isinstance(namespace_items[-1], NamespaceInfo)
            assert isinstance(namespace_items[-1].parser_info, (IfStatementClauseParserInfo, IfStatementElseClauseParserInfo))

            source_info = cast(NamespaceInfo, namespace_items.pop())
            namespace_items.pop()

            if not namespace_items:
                del self._namespace_infos[-1].children[None]

            self._namespace_infos[-1].AugmentChildren(source_info.children)

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
    # |  ImportStatementParserInfo
    # ----------------------------------------------------------------------
    @contextmanager
    def OnImportStatementParserInfo(
        self,
        parser_info: ImportStatementParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnImportStatementItemParserInfo(
        self,
        parser_info: ImportStatementItemParserInfo,
    ):
        yield

    # ----------------------------------------------------------------------
    # |  PassStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnPassStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # |  SpecialMethodStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnSpecialMethodStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # |  TypeAliasStatementParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTypeAliasStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _PostProcessIfClause(self) -> None:
        assert isinstance(self._namespace_infos[-1], NamespaceInfo)
        assert isinstance(self._namespace_infos[-1].parser_info, (IfStatementClauseParserInfo, IfStatementElseClauseParserInfo))

        # Skip all the if-related stuff
        assert len(self._namespace_infos) > 2

        index = -2

        while True:
            assert isinstance(self._namespace_infos[index], NamespaceInfo)

            if not isinstance(
                self._namespace_infos[index].parser_info,
                (
                    IfStatementParserInfo,
                    IfStatementClauseParserInfo,
                    IfStatementElseClauseParserInfo,
                ),
            ):
                break

            index -= 1

            assert -index != len(self._namespace_infos)

        assert isinstance(self._namespace_infos[index], NamespaceInfo)
        self._namespace_infos[index].AugmentChildren(self._namespace_infos[-1].children)

    # ----------------------------------------------------------------------
    def _RemoveStatementFromParentNamespace(
        self,
        key_name: Optional[str]=None,
    ) -> None:
        assert len(self._namespace_infos) >= 2

        child = self._namespace_infos[-1]
        parent = self._namespace_infos[-2]

        if isinstance(child, ParserInfo):
            parser_info = child
        elif isinstance(child, NamespaceInfo):
            parser_info = child.parser_info
        else:
            assert False, child  # pragma: no cover

        assert isinstance(parent, NamespaceInfo), parent

        if isinstance(parent.children[key_name], list):
            parent_items = cast(List[Union[NamespaceInfo, ParserInfo]], parent.children[key_name])
            assert parser_info == cast(NamespaceInfo, parent_items[-1]).parser_info

            parent_items.pop()

            if len(parent_items) == 1:
                parent.children[key_name] = parent_items[0]
        else:
            assert parser_info == cast(NamespaceInfo, parent.children[key_name]).parser_info
            del parent.children[key_name]
