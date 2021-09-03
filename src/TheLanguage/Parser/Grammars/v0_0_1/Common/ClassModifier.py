# ----------------------------------------------------------------------
# |
# |  ClassModifier.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-02 12:10:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the FileModifier object"""

import os

from enum import auto
from typing import cast

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Impl.ModifierBase import ModifierBase


# ----------------------------------------------------------------------
class ClassModifier(ModifierBase):
    """\
    Modifies the mutability of a method or attribute.
    """

    immutable                               = auto()
    mutable                                 = auto()
