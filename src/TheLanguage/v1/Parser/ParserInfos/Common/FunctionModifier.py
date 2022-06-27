# ----------------------------------------------------------------------
# |
# |  FunctionModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-27 10:41:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the function modifier object"""

import os

from enum import auto, Enum

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class FunctionModifier(Enum):
    generator                               = auto()
    reentrant                               = auto()
    scoped                                  = auto()
    standard                                = auto()
