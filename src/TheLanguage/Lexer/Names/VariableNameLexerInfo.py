# ----------------------------------------------------------------------
# |
# |  VariableNameLexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-08 14:30:06
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableNameLexerInfo object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NameLexerInfo import NameLexerInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableNameLexerInfo(NameLexerInfo):
    Name: str

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        assert self.Name
        super(VariableNameLexerInfo, self).__post_init__(regions)
