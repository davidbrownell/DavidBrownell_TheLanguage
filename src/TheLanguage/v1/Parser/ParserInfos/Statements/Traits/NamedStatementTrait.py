# ----------------------------------------------------------------------
# |
# |  NamedStatementTrait.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-17 12:47:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NamedStatementTrait object"""

import os

from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common.VisibilityModifier import VisibilityModifier


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NamedStatementTrait(object):
    """Adds a name to the namespace"""

    # ----------------------------------------------------------------------
    name: str

    visibility_param: InitVar[VisibilityModifier]
    visibility: VisibilityModifier          = field(init=False)

    allow_name_to_be_duplicated__: bool     = field(init=False, default=False)
    name_is_ordered__: bool                 = field(init=False, default=True)

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility_param):
        object.__setattr__(self, "visibility", visibility_param)

    # ----------------------------------------------------------------------
    @staticmethod
    def RegionlessAttributesArgs() -> List[str]:
        return [
            "allow_name_to_be_duplicated__",
            "name_is_ordered__",
        ]

    # ----------------------------------------------------------------------
    @staticmethod
    def ObjectReprImplBaseInitKwargs() -> Dict[str, Any]:
        return {
            "allow_name_to_be_duplicated__": None,
            "name_is_ordered__": None,
        }

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _InitTraits(
        self,
        *,
        allow_name_to_be_duplicated: Optional[bool]=None,
        name_is_ordered: Optional[bool]=None,
    ) -> None:
        if allow_name_to_be_duplicated is not None:
            object.__setattr__(self, "allow_name_to_be_duplicated__", allow_name_to_be_duplicated)
        if name_is_ordered is not None:
            object.__setattr__(self, "name_is_ordered__", name_is_ordered)
