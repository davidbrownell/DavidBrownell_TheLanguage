# ----------------------------------------------------------------------
# |
# |  TypeModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 10:40:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeModifier enum"""

import os

from enum import auto, IntFlag

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class TypeModifier(IntFlag):
    """\
    Modifies the behavior of a type.

    |-----------|----------|--------|
    |           | isolated | shared |
    |-----------|----------|--------|
    | mutable   |    var   |   ref  |
    | immutable |    val   |  view  |
    |-----------|----------|--------|
    """

    _mutable                                = auto()
    _immutable                              = auto()
    _isolated                               = auto()
    _shared                                 = auto()

    mutable                                 = (_mutable << 4)
    immutable                               = (_immutable << 4)
    isolated                                = (_isolated << 4)
    shared                                  = (_shared << 4)

    var                                     = mutable | isolated
    ref                                     = mutable | shared
    val                                     = immutable | isolated
    view                                    = immutable | shared
