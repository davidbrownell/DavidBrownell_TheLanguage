# ----------------------------------------------------------------------
# |
# |  VariableNameParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 13:02:01
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariableNameParserInfo object"""

import os

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NameParserInfo import NameParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariableNameParserInfo(NameParserInfo):
    Name: str

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        assert self.Name
        super(VariableNameParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Name"],
        )
