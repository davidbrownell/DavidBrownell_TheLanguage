# ----------------------------------------------------------------------
# |
# |  VisibilityModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-07 15:05:18
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VisibilityModifier object"""

import os

from enum import auto, Enum

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class VisibilityModifier(Enum):
    """\
    Modifies the external visibility of a function, method, class attribute, etc.
    """

    private                                 = auto()
    protected                               = auto()
    public                                  = auto()
