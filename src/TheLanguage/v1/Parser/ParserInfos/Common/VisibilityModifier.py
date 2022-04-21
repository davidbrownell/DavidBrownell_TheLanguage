# ----------------------------------------------------------------------
# |
# |  VisibilityModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-03-15 20:35:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
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
    private                                 = auto()
    protected                               = auto()
    internal                                = auto()
    public                                  = auto()

    # TODO: Validate the protected is used appropriately
