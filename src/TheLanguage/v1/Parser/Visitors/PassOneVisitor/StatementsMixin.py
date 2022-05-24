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
from typing import cast, List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ..NamespaceInfo import ParsedNamespaceInfo

    from ...Error import CreateError
    from ...Helpers import MiniLanguageHelpers

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
        if parser_info.parser_info_type__ != ParserInfoType.Configuration:
            # Ensure that the statement is only used where it is allowed
            parent_scope_flag = self._namespaces[-1].scope_flag

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

        MiniLanguageHelpers.EvalExpression(parser_info.expression, self._configuration_info)

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ):
        assert self._namespaces

        if parser_info.parser_info_type__ != ParserInfoType.Configuration:
            # Ensure that the statement is only used where it is allowed
            parent_scope_flag = self._namespaces[-1].scope_flag

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
        true_clause_name: Optional[str] = None

        for clause in parser_info.clauses:
            execute_flag = False

            if true_clause_name is None:
                clause_result = MiniLanguageHelpers.EvalExpression(clause.expression, self._configuration_info)
                clause_result = clause_result.type.ToBoolValue(clause_result.value)

                if clause_result:
                    true_clause_name = clause.name
                    execute_flag = True

            if not execute_flag:
                clause.Disable()

        if parser_info.else_clause and true_clause_name is not None:
            parser_info.else_clause.Disable()

        yield

        if true_clause_name is not None:
            # Move everything from the if clause to the parent namespace
            clause_namespace = self._namespaces[-1].children[true_clause_name]
            assert isinstance(clause_namespace, ParsedNamespaceInfo)

            for namespace in clause_namespace.children.values():
                self._AddNamespaceItem(namespace)
