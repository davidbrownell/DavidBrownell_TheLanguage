# ----------------------------------------------------------------------
# |
# |  TypeModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-11 12:50:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality associated with type modifiers"""

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

    mutable                                 = auto()
    immutable                               = auto()
    isolated                                = auto()
    shared                                  = auto()

    var                                     = (mutable << 4) | isolated
    ref                                     = (mutable << 4) | shared
    val                                     = (immutable << 4) | isolated
    view                                    = (immutable << 4) | shared

    # ----------------------------------------------------------------------
    @classmethod
    def CreatePhraseItem(cls):
        return tuple(e.name for e in cls)
