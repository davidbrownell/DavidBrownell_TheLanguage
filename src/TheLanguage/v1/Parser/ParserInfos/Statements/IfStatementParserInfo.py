# ----------------------------------------------------------------------
# |
# |  IfStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-21 14:32:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IfStatementParserInfo and IfStatementClauseParserInfo objects"""

import os

from typing import cast, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import (
        ParserInfo,
        ParserInfoType,
        Region,
        ScopeFlag,
        StatementParserInfo,
    )

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementClauseParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    introduces_scope__                      = True

    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[Region]]]

    expression: ExpressionParserInfo
    statements: List[StatementParserInfo]
    documentation: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        expression: ExpressionParserInfo,
        statements: List[StatementParserInfo],
        *args,
        **kwargs,
    ):
        parser_info_type = expression.parser_info_type__

        # If the expression is ambiguous, see if we can get some context from the statements
        if parser_info_type == ParserInfoType.Unknown:
            for statement in statements:
                if (
                    parser_info_type == ParserInfoType.Unknown
                    or statement.parser_info_type__.value < parser_info_type.value
                ):
                    parser_info_type = statement.parser_info_type__

        return cls(
            parser_info_type,               # type: ignore
            regions,                        # type: ignore
            expression,
            statements,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(IfStatementClauseParserInfo, self).__init__(
            *args,
            **kwargs,
            regionless_attributes=["expression", ],
        )

        self.expression.ValidateAsExpression()

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[
                ("expression", self.expression),
            ],
            children=cast(List[ParserInfo], self.statements),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementElseClauseParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    introduces_scope__                      = True

    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    statements: List[StatementParserInfo]
    documentation: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions, *args, **kwargs):
        super(IfStatementElseClauseParserInfo, self).__init__(
            ParserInfoType.Unknown,
            regions,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=None,
            children=cast(List[ParserInfo], self.statements),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementParserInfo(StatementParserInfo):
    # ----------------------------------------------------------------------
    clauses: List[IfStatementClauseParserInfo]
    else_clause: Optional[IfStatementElseClauseParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        clauses: List[IfStatementClauseParserInfo],
        *args,
        **kwargs,
    ):
        return cls(
            ScopeFlag.Root | ScopeFlag.Class | ScopeFlag.Function,
            ParserInfoType.GetDominantType(*clauses),   # type: ignore
            regions,                                    # type: ignore
            clauses,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(IfStatementParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=[
                "clauses",
                "else_clause",
            ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=None,
            children=cast(List[ParserInfo], self.clauses) + cast(List[ParserInfo], [self.else_clause] if self.else_clause else []),
        )
