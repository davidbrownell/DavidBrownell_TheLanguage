# ----------------------------------------------------------------------
# |
# |  MutabilityModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 12:26:51
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MutabilityModifier object"""

import os

from enum import auto, Flag

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class MutabilityModifier(Flag):
    var                                     = auto()
    ref                                     = auto()
    val                                     = auto()

    mutable                                 = var | ref
    immutable                               = val
