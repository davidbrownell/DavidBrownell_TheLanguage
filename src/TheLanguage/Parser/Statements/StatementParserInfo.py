#
# |  StatementParserInfo.py
# |
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StatementParserData and StatementParserInfo objects"""

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
    from ..ParserInfo import ParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StatementParserInfo(ParserInfo, Interface.Interface):
    """Abstract base class for all statement-related lexer info"""

    pass
