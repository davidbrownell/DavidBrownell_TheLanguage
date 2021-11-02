# ----------------------------------------------------------------------
# |
# |  StatementParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 10:13:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StatementParserInfo object"""

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
    """Abstract base class for all statement-related parser info objects"""

    pass
