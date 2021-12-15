# ----------------------------------------------------------------------
# |
# |  MethodModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-15 10:49:31
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MethodModifier enum"""

import os

from enum import auto, Enum

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class MethodModifier(Enum):
    """Modifies how a method should be consumed"""

    abstract                                = auto()
    final                                   = auto()
    override                                = auto()
    standard                                = auto()
    static                                  = auto() # TODO: Move static, should be a class modifier
    virtual                                 = auto()
