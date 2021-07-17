# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-16 10:59:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains utilities used by multiple statements and expressions"""

import os

from typing import cast, Match

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....ParserImpl.Token import Token

    from ...GrammarStatement import (
        Leaf,
        Statement,
    )



# ----------------------------------------------------------------------
def GetRegexMatch(
    leaf: Leaf,
) -> Match:
    return cast(
        Token.RegexMatch,
        leaf.Value,
    ).Match
