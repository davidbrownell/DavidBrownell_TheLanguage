#
# |  StatementLexerInfo.py
# |
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StatementLexerData and StatementLexerInfo objects"""

import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..LexerInfo import LexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StatementLexerInfo(LexerInfo, Interface.Interface):
    """Abstract base class for all statement-related lexer info"""

    pass
