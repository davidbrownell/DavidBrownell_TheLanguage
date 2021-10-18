# ----------------------------------------------------------------------
# |
# |  TryStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-14 11:13:11
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TryStatementParserInfo object"""

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
class TryStatementClauseParserInfo(ParserInfo):
    Type: TypeParserInfo
    Name: Optional[str]
    Statements: List[StatementParserInfo]


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TryStatementParserInfo(StatementParserInfo):
    TryStatements: List[StatementParserInfo]
    ExceptClauses: Optional[List[TryStatementClauseParserInfo]]
    DefaultStatements: Optional[List[StatementParserInfo]]
