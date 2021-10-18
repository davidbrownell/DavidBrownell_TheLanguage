# ----------------------------------------------------------------------
# |
# |  IfStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 16:17:43
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the IfStatementParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import ParserInfo, StatementParserInfo
    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementClauseParserInfo(ParserInfo):
    Condition: ExpressionParserInfo
    Statements: List[StatementParserInfo]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class IfStatementParserInfo(StatementParserInfo):
    Clauses: List[IfStatementClauseParserInfo]
    ElseStatements: Optional[List[StatementParserInfo]]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(IfStatementParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Clauses"],
        )
