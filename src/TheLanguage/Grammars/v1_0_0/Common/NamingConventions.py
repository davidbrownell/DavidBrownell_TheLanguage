# ----------------------------------------------------------------------
# |
# |  NamingConventions.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-16 19:48:33
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Various naming conventions enforced automatically"""

import os
import re

from dataclasses import dataclass
from typing import List, Pattern

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _NamingConvention(object):
    Regex: Pattern
    Constraints: List[str]


# ----------------------------------------------------------------------
Class                                       = _NamingConvention(
    re.compile(
        r"""(?#
            [Optional] Underscore           )_?(?#
            Uppercase                       )[A-Z](?#
            Alpha-numeric and underscore    )[A-Za-z0-9_]+(?#
        )""",
    ),
    [
        "Begin with an uppercase letter",
        "Contain upper-, lower-, numeric-, or underscore-characters",
        "Contain at least 2 characters",
    ],
)


# ----------------------------------------------------------------------
Function                                    = _NamingConvention(
    re.compile(
        r"""(?#
            [Optional] Underscore           )_?(?#
            Uppercase                       )[A-Z](?#
            Alpha-numeric and underscore    )[A-Za-z0-9_]+(?#
            [Optional] Async Decorator      )(?:\.\.\.)?(?#
            [Optional] Partial Decorator    )\??(?#
        )""",
    ),
    [
        "Begin with an uppercase letter",
        "Contain upper-, lower-, numeric-, or underscore-characters",
        "Contain 2 or more characters",
    ],
)


# ----------------------------------------------------------------------
Variable                                    = _NamingConvention(
    re.compile(
        r"""(?#
            [Optional] Underscore           )_?(?#
            Lowercase                       )[a-z](?#
            Alpha-numeric and underscore    )[a-zA-Z0-9_]*(?#
        )""",
    ),
    [
        "Begin with a lowercase letter",
        "Contain upper-, lower-, numeric-, or underscore-characters",
    ],
)
