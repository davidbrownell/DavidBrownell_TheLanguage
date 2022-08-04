# ----------------------------------------------------------------------
# |
# |  ConstrainedStatementTrait.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-19 08:06:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ConstrainedStatementTrait object"""

import os

from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstrainedStatementTrait(Interface.Interface):
    """Apply to statements that can have constraints"""

    # ----------------------------------------------------------------------
    # |  Public Data
    constraints_param: InitVar[Optional[ConstraintParametersParserInfo]]
    constraints: Optional[ConstraintParametersParserInfo]                   = field(init=False, default=None)

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self, constraints_param):
        object.__setattr__(self, "constraints", constraints_param)

    # ----------------------------------------------------------------------
    @staticmethod
    def RegionlessAttributesArgs() -> List[str]:
        return [
            "constraints",
        ]

    # ----------------------------------------------------------------------
    @staticmethod
    def ObjectReprImplBaseInitKwargs() -> Dict[str, Any]:
        return {}
