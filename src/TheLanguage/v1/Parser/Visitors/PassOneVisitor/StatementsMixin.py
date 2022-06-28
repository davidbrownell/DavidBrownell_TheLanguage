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
    from ..NamespaceInfo import ParsedNamespaceInfo

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Statements.FuncInvocationStatementParserInfo import FuncInvocationStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo
    from ...ParserInfos.Statements.PassStatementParserInfo import PassStatementParserInfo


# ----------------------------------------------------------------------
class StatementsMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @contextmanager
    def OnFuncInvocationStatementParserInfo(
        self,
        parser_info: FuncInvocationStatementParserInfo,
    ):
        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)
            MiniLanguageHelpers.EvalExpression(parser_info.expression, [self._configuration_info])

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnIfStatementParserInfo(
        self,
        parser_info: IfStatementParserInfo,
    ):
        true_clause_name: Optional[str] = None

        if parser_info.parser_info_type__ == ParserInfoType.Configuration:
            self._FlagAsProcessed(parser_info)

            for clause in parser_info.clauses:
                self._FlagAsProcessed(clause)

                execute_flag = False

                if true_clause_name is None:
                    clause_result = MiniLanguageHelpers.EvalExpression(
                        clause.expression,
                        [self._configuration_info],
                    )

                    clause_result = clause_result.type.ToBoolValue(clause_result.value)
                    if clause_result:
                        true_clause_name = clause.name
                        execute_flag = True

                if not execute_flag:
                    clause.Disable()

            if parser_info.else_clause:
                self._FlagAsProcessed(parser_info.else_clause)

                if true_clause_name is not None:
                    parser_info.else_clause.Disable()

        yield

        if true_clause_name is not None:
            # Move everything from the if clause to the parent namespace
            clause_namespace = self._namespace_stack[-1].children[true_clause_name]
            assert isinstance(clause_namespace, ParsedNamespaceInfo)

            for namespace in clause_namespace.children.values():
                self._AddNamespaceItem(namespace)

    # ----------------------------------------------------------------------
    @contextmanager
    def OnPassStatementParserInfo(
        self,
        parser_info: PassStatementParserInfo,
    ):
        parser_info.Disable()
        yield VisitResult.SkipAll
