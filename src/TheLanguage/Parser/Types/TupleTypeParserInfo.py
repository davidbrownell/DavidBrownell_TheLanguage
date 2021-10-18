# ----------------------------------------------------------------------
# |
# |  TupleTypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-12 11:15:19
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleTypeParserInfo object"""

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
    from .TypeParserInfo import TypeParserInfo
    from ..Common.VisitorTools import StackHelper, VisitType


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleTypeParserInfo(TypeParserInfo):
    Types: List[TypeParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(TupleTypeParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Types"],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor, stack, *args, **kwargs):
        results = []

        results.append(visitor.OnTupleType(stack, VisitType.PreChildEnumeration, self, *args, **kwargs))

        with StackHelper(stack)[(self, "Types")] as helper:
            results.append([the_type.Accept(visitor, helper.stack, *args, **kwargs) for the_type in self.Types])

        results.append(visitor.OnTupleType(stack, VisitType.PostChildEnumeration, self, *args, **kwargs))

        return results
