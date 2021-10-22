# ----------------------------------------------------------------------
# |
# |  TupleNameParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 10:55:30
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleNameParserInfo object"""

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
    from .NameParserInfo import NameParserInfo
    from ..Common.VisitorTools import StackHelper, VisitType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleNameParserInfo(NameParserInfo):
    Names: List[NameParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(TupleNameParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Names"],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        if visitor.OnTupleName(stack, VisitType.Enter, self, *args, **kwargs) is False:
            return

        with StackHelper(stack)[(self, "Names")] as helper:
            for name in self.Names:
                name.Accept(visitor, helper.stack, *args, **kwargs)

        visitor.OnTupleName(stack, VisitType.Exit, self, *args, **kwargs)
