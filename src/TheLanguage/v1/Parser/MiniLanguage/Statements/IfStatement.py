# ----------------------------------------------------------------------
# |
# |  IfStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-17 09:29:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IfStatement and IfStatementClause objects"""

import copy
import os

from typing import Any, Dict, List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Statement import Statement, Type
    from ..Expressions.Expression import Expression


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementClause(ObjectReprImplBase):
    condition: Expression
    statements: List[Statement]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.statements


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatement(Statement):
    clauses: List[IfStatementClause]
    else_statements: Optional[List[Statement]]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.else_statements is None or self.else_statements

        super(IfStatement, self).__init__()

    # ----------------------------------------------------------------------
    @Interface.override
    def Execute(
        self,
        args: Dict[str, Any],
        type_overloads: Dict[str, Type],
    ) -> Statement.ExecuteResult:
        for clause in self.clauses:
            clause_type_overloads = copy.deepcopy(type_overloads)

            result = clause.condition.Eval(args, clause_type_overloads)
            if not result.type.ToBoolValue(result.value):
                continue

            return self.__class__._Execute(clause.statements, args, clause_type_overloads)  # pylint: disable=protected-access

        if self.else_statements is not None:
            return self.__class__._Execute(self.else_statements, args, type_overloads)  # pylint: disable=protected-access

        return Statement.ExecuteResult(
            errors=[],
            warnings=[],
            infos=[],
            should_continue=True,
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _Execute(
        statements: List[Statement],
        args: Dict[str, Any],
        type_overloads: Dict[str, Type],
    ) -> Statement.ExecuteResult:
        errors: List[str] = []
        warnings: List[str] = []
        infos: List[str] = []

        should_continue = True

        for statement in statements:
            result = statement.Execute(args, type_overloads)

            errors += result.errors
            warnings += result.warnings
            infos += result.infos

            should_continue = result.should_continue
            if not should_continue:
                break

        return Statement.ExecuteResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
            should_continue=should_continue,
        )
