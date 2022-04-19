# ----------------------------------------------------------------------
# |
# |  VariantCompileTypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-17 12:25:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the VariantCompileTypeParserInfo object"""

import os

from typing import List

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .CompileTypeParserInfo import CompileTypeParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class VariantCompileTypeParserInfo(CompileTypeParserInfo):
    items: List[CompileTypeParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(VariantCompileTypeParserInfo, self).__post_init__(
            regions,
            regionless_attributes=[
                "type",
            ],
        )
