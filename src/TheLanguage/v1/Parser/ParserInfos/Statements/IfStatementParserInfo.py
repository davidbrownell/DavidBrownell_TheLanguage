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

from typing import List, Optional

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
        StatementParserInfo,
    )

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementClauseParserInfo(ParserInfo):
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
        *args,
        **kwargs,
    ):
        return cls(
            expression.parser_info_type__,  # type: ignore
            regions,                        # type: ignore
            expression,
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


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementParserInfo(StatementParserInfo):
    # ----------------------------------------------------------------------
    clauses: List[IfStatementClauseParserInfo]
    else_statements: Optional[List[StatementParserInfo]]
    else_documentation: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        clauses: List[IfStatementClauseParserInfo],
        *args,
        **kwargs,
    ):
        parse_info_type = cls._GetDominantExpressionType(*clauses)
        if isinstance(parse_info_type, list):
            raise ErrorException(*parse_info_type)

        return cls(
            parse_info_type,                # type: ignore
            regions,                        # type: ignore
            clauses,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        assert self.else_documentation is None or self.else_statements is not None

        super(IfStatementParserInfo, self).__post_init__(
            *args,
            **kwargs,
            regionless_attributes=["clauses", ],
        )
