# ----------------------------------------------------------------------
# |
# |  StatementsMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-10 13:21:00
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
from typing import cast, List

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
    from ...NamespaceInfo import ParsedNamespaceInfo

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo, IfStatementClauseParserInfo, IfStatementElseClauseParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import ScopeFlag


# ----------------------------------------------------------------------
InvalidIfStatementScopeError                = CreateError(
    "If statements without compile-time expressions are not valid at this level",
)


# ----------------------------------------------------------------------
class StatementsMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncInvocationStatementParserInfo(
        self,
        parser_info: FuncInvocationStatementParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            MiniLanguageHelpers.EvalExpression(parser_info.expression, self._configuration_info)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ):
        assert self._namespace_infos

        if parser_info.parser_info_type__ != ParserInfoType.Configuration:
            # Ensure that the statement is only used where it is allowed
            parent_scope_flag = self._namespace_infos[-1].scope_flag

            if (
                (parser_info.parser_info_type__ == ParserInfoType.TypeCustomization and parent_scope_flag == ScopeFlag.Root)
                or (parser_info.parser_info_type__ == ParserInfoType.Standard and parent_scope_flag != ScopeFlag.Function)
            ):
                self._errors.append(
                    InvalidIfStatementScopeError.Create(
                        region=parser_info.regions__.self__,
                    ),
                )

                yield VisitResult.SkipAll

            else:
                yield

            return

        # Determine which clause evaluates to true
        found_true_clause = False

        for clause in parser_info.clauses:
            execute_flag = False

            if not found_true_clause:
                clause_result = MiniLanguageHelpers.EvalExpression(clause.expression, self._configuration_info)
                clause_result = clause_result.type.ToBoolValue(clause_result.value)

                if clause_result:
                    found_true_clause = True
                    execute_flag = True

            self.__class__._SetExecuteFlag(clause, execute_flag)  # pylint: disable=protected-access

        if parser_info.else_clause:
            self.__class__._SetExecuteFlag(parser_info.else_clause, not found_true_clause)  # pylint: disable=protected-access

        yield

        if found_true_clause:
            # Move everything from the if clause to the proper namespace
            assert isinstance(self._namespace_infos[-1], ParsedNamespaceInfo)
            assert None in self._namespace_infos[-1].children
            assert isinstance(self._namespace_infos[-1].children[None], list)

            namespace_items = cast(List[ParsedNamespaceInfo], self._namespace_infos[-1].children[None])
            assert len(namespace_items) >= 2
            assert isinstance(namespace_items[-1].parser_info, (IfStatementClauseParserInfo, IfStatementElseClauseParserInfo))
            assert isinstance(namespace_items[-2].parser_info, IfStatementParserInfo)

            source_info = namespace_items.pop()         # IfStatementClauseParserInfo | IfStatementElseClauseParserInfo
            namespace_items.pop()                       # IfStatementParserInfo

            if not namespace_items:
                del self._namespace_infos[-1].children[None]

            self._namespace_infos[-1].AugmentChildren(source_info.children)
