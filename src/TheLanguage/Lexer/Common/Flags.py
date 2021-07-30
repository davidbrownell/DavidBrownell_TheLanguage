# ----------------------------------------------------------------------
# |
# |  Flags.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-29 10:34:04
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains flag definitions common to multiple Node definitions"""

import os

from enum import auto, Enum, IntFlag

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class VisibilityType(Enum):
    """Controls how functionality is made available in a variety of different contexts."""

    # The meaning of these values is dependent upon context; when used with...
    #
    #   Class and Function definitions:
    #       Private:    Visible within the file it was defined in.
    #       Protected:  Visible within the source directory
    #       Public:     Visible anywhere
    #
    #   Class inheritance:
    #       Private:    Base functionality is only available to the current class
    #       Protected:  Base functionality is available to all derived classes
    #       Public:     Base functionality is available anywhere

    Private                                 = auto()
    Protected                               = auto()
    Public                                  = auto()


# ----------------------------------------------------------------------
class TypeFlags(IntFlag):
    """\
    TODO: Comment
    """

    Mutable                                 = auto()
    Immutable                               = auto()

    Isolated                                = auto()
    Shared                                  = auto()


# ----------------------------------------------------------------------
class FunctionFlags(IntFlag):
    """\
    TODO: Comment
    """

    IsPartial                               = auto()    # Flag set if the function generates exceptions.
    IsCoroutine                             = auto()    # Flag set if the function is a coroutine/generator.


# ----------------------------------------------------------------------
class OperatorCategory(IntFlag):
    """\
    TODO: Comment
    """

    Logical                                 = auto()
    Comparison                              = auto()
    Math                                    = auto()
    BitManipulation                         = auto()
