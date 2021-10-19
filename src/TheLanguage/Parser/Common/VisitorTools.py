# ----------------------------------------------------------------------
# |
# |  VisitTools.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-18 08:25:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains tools that help when writing visitors"""

import os

from contextlib import contextmanager
from enum import auto, Enum

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class VisitType(Enum):
    """Indicates when an On____ function is being invoked for a visitor."""

    PreChildEnumeration                     = auto()
    PostChildEnumeration                    = auto()
    NoChildEnumeration                      = auto()


# ----------------------------------------------------------------------
class StackHelper(object):
    # ----------------------------------------------------------------------
    def __init__(self, stack):
        self.stack                          = stack

    # ----------------------------------------------------------------------
    @contextmanager
    def __getitem__(self, index):
        self.stack.push(index)

        try:
            yield self
        finally:
            self.stack.pop()
