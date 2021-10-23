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

from typing import List

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
    from .Common.VisitorTools import StackHelper, VisitType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class RootParserInfo(ParserInfo):
    Statements: List[ParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(RootParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Statements"],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnRoot(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[(self, "Statements")] as helper:
            for statement in self.Statements:
                statement.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnRoot(stack, VisitType.Exit, self, *args, **kwargs)
