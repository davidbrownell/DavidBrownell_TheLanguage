# ----------------------------------------------------------------------
# |
# |  TryExceptStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-16 11:26:26
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TryExceptStatementParserInfo object"""

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
    from ..Types.TypeParserInfo import TypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TryExceptStatementClauseParserInfo(ParserInfo):
    Type: TypeParserInfo
    Name: str
    Statements: List[StatementParserInfo]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TryExceptStatementParserInfo(StatementParserInfo):
    TryStatements: List[StatementParserInfo]
    ExceptClauses: Optional[List[TryExceptStatementClauseParserInfo]]
    DefaultStatements: Optional[List[StatementParserInfo]]