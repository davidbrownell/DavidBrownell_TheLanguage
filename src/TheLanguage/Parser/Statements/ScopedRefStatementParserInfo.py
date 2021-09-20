# ----------------------------------------------------------------------
# |
# |  ScopedRefStatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-16 10:46:59
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ScopedRefStatementParserInfo object"""

import os

from typing import List

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StatementParserInfo import StatementParserInfo
    from ..Names.VariableNameParserInfo import VariableNameParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ScopedRefStatementParserInfo(StatementParserInfo):
    Variables: List[VariableNameParserInfo]
    Statements: List[StatementParserInfo]
