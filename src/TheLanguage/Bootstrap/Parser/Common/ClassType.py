# ----------------------------------------------------------------------
# |
# |  ClassType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-15 10:48:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassType enum"""

import os

from enum import Enum

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class ClassType(Enum):
    Class                                   = "class"
    Enum                                    = "enum"
    Exception                               = "exception"
    Interface                               = "interface"
    Mixin                                   = "mixin"
    Struct                                  = "struct"
    Trait                                   = "trait"
