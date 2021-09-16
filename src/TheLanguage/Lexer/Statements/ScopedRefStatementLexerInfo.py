# ----------------------------------------------------------------------
# |
# |  ScopedRefStatementLexerInfo.py
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
"""Contains the ScopedRefStatementLexerInfo object"""

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
    from .StatementLexerInfo import StatementLexerInfo
    from ..Names.VariableNameLexerInfo import VariableNameLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ScopedRefStatementLexerInfo(StatementLexerInfo):
    Variables: List[VariableNameLexerInfo]
    Statements: List[StatementLexerInfo]
