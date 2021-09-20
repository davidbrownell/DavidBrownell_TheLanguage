# ----------------------------------------------------------------------
# |
# |  ClassModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-07 15:27:09
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ClassModifier object"""

import os

from enum import auto, Enum

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class ClassModifier(Enum):
    """\
    Modifies the mutability of a method or attribute.
    """

    immutable                               = auto()
    mutable                                 = auto()
