# ----------------------------------------------------------------------
# |
# |  CharacterLiteralParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-28 14:40:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CharacterLiteralParserInfo object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .LiteralParserInfo import LiteralParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CharacterLiteralParserInfo(LiteralParserInfo):
    Value: str

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(CharacterLiteralParserInfo, self).__post_init__(regions)

        assert len(self.Value) <= 2, self.Value
