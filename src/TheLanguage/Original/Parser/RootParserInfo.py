# ----------------------------------------------------------------------
# |
# |  RootParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-30 15:00:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the RootParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ParserInfo import ParserInfo
    from .Common.VisitorTools import StackHelper


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class RootParserInfo(ParserInfo):
    Statements: List[ParserInfo]
    Documentation: Optional[str]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(RootParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Statements"],
        )

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[(self, "Statements")] as helper:
            for statement in self.Statements:
                statement.Accept(visitor, helper.stack, *args, **kwargs)
