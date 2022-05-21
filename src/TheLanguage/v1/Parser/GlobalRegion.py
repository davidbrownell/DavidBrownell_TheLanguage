# ----------------------------------------------------------------------
# |
# |  GlobalRegion.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-19 10:40:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GlobalRegion object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class GlobalRegion(TranslationUnitRegion):
    """Region within a file"""

    workspace_name: str
    relative_name: str

    # ----------------------------------------------------------------------
    def __contains__(self, other):
        return (
            self.workspace_name == other.workspace_name
            and self.relative_name == other.relative_name
            and super(GlobalRegion, self).__contains__(other)
        )

    # ----------------------------------------------------------------------
    @classmethod
    def Compare(cls, value1, value2):
        if value1.workspace_name < value2.workspace_name:
            return -1
        if value1.workspace_name > value2.workspace_name:
            return 1

        if value1.relative_name < value2.relative_name:
            return -1
        if value1.relative_name > value2.relative_name:
            return 1

        return super(GlobalRegion, cls).Compare(value1, value2)
