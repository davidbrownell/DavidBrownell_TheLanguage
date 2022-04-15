# ----------------------------------------------------------------------
# |
# |  CharacterLiteral.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 12:00:17
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CharacterLiteral object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .LiteralPhrase import LiteralPhrase


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CharacterLiteral(LiteralPhrase):
    value: int

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(CharacterLiteral, self).__post_init__(regions)
