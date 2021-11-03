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

from typing import List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeParserInfo import TypeParserInfo, Region

    from ..Common.TypeModifier import TypeModifier
    from ..Common.VisitorTools import StackHelper


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleTypeParserInfo(TypeParserInfo):
    Types: List[TypeParserInfo]
    Modifier: Optional[TypeModifier]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(TupleTypeParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Types"],
        )

        for the_type in self.Types:
            modifier = the_type.GetTypeModifier()
            if modifier is not None:
                raise Exception("BugBug - type modifiers must be Noen")

    # ----------------------------------------------------------------------
    @Interface.override
    def GetTypeModifier(self) -> Optional[Tuple[TypeModifier, Region]]:
        """Returns information a TypeModifier associated with the type (if any)"""

        if self.Modifier is None:
            return None

        return (self.Modifier, self.Regions__.Modifier)  # type: ignore && pylint: disable=no-member

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _AcceptImpl(self, visitor, stack, *args, **kwargs):
        with StackHelper(stack)[(self, "Types")] as helper:
            for the_type in self.Types:
                the_type.Accept(visitor, helper.stack, *args, **kwargs)
