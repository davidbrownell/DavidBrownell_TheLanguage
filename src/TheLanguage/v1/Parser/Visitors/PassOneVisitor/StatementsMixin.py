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

    from ...Error import CreateError

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo, IfStatementClauseParserInfo, IfStatementElseClauseParserInfo


# ----------------------------------------------------------------------
InvalidFuncInvocationStatementScopeError    = CreateError(
    "Function invocations without compile-time expressions are not valid at this level",
)

InvalidIfStatementScopeError                = CreateError(
    "If statements without compile-time expressions are not valid at this level",
)


# ----------------------------------------------------------------------
class StatementsMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @contextmanager
    def OnClassStatementParserInfo(
        self,
        parser_info: ClassStatementParserInfo,
    ):
        assert self._namespace_stack
        namespace = self._namespace_stack[-1]

        assert isinstance(namespace, ParsedNamespaceInfo), namespace
        assert namespace.parser_info == parser_info, namespace.parser_info

        assert "ThisType" not in namespace.children
        namespace.children["ThisType"] = ParsedNamespaceInfo(
            namespace,
            ScopeFlag.Class | ScopeFlag.Function,
            parser_info,
            children=None,
            visibility=VisibilityModifier.private,
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncInvocationStatementParserInfo(
        self,
        parser_info: FuncInvocationStatementParserInfo,
    ):
        # BugBug: If method, add "this" and "self"

        if parser_info.parser_info_type__ != ParserInfoType.Configuration:
            # Ensure that the statement is only used where it is allowed
            parent_scope_flag = self._namespace_stack[-1].scope_flag

            if (
                (parser_info.parser_info_type__ == ParserInfoType.TypeCustomization and parent_scope_flag == ScopeFlag.Root)
                or (parser_info.parser_info_type__ == ParserInfoType.Standard and parent_scope_flag != ScopeFlag.Function)
            ):
                self._errors.append(
                    InvalidFuncInvocationStatementScopeError.Create(
                        region=parser_info.regions__.self__,
                    ),
                )

                yield VisitResult.SkipAll

            else:
                yield

            return

        MiniLanguageHelpers.EvalExpression(
            parser_info.expression,
            self._configuration_info,
            [],
        )

        parser_info.SetValidatedFlag()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ):
        assert self._namespace_stack

        if parser_info.parser_info_type__ != ParserInfoType.Configuration:
            # Ensure that the statement is only used where it is allowed
            parent_scope_flag = self._namespace_stack[-1].scope_flag

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
                clause_result = MiniLanguageHelpers.EvalExpression(
                    clause.expression,
                    self._configuration_info,
                    [],
                )

                clause_result = clause_result.type.ToBoolValue(clause_result.value)

                if clause_result:
                    true_clause_name = clause.name
                    execute_flag = True

            if not execute_flag:
                clause.Disable()

            clause.SetValidatedFlag()

        if parser_info.else_clause:
            if true_clause_name is not None:
                parser_info.else_clause.Disable()

            parser_info.else_clause.SetValidatedFlag()

        parser_info.SetValidatedFlag()

        yield

        if true_clause_name is not None:
            # Move everything from the if clause to the parent namespace
            clause_namespace = self._namespace_stack[-1].children[true_clause_name]
            assert isinstance(clause_namespace, ParsedNamespaceInfo)

            for namespace in clause_namespace.children.values():
                self._AddNamespaceItem(namespace)

    # BugBug: On Special methods, add "this" and/or "self"?
