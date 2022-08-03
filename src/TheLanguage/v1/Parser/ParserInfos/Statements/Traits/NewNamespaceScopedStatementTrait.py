# ----------------------------------------------------------------------
# |
# |  NewNamespaceScopedStatementTrait.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-06-17 12:50:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NewNamespaceScopedStatementTrait object"""

import os

from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ScopedStatementTrait import ScopedStatementTrait


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NewNamespaceScopedStatementTrait(ScopedStatementTrait):
    """Add to statements to introduce new scoping rules"""

    # ----------------------------------------------------------------------
    allow_duplicate_names__: bool            = field(init=False, default=False)

    # ----------------------------------------------------------------------
    @classmethod
    def RegionlessAttributesArgs(cls) -> List[str]:
        return [
            "allow_duplicate_names__",
        ] + ScopedStatementTrait.RegionlessAttributesArgs()

    # ----------------------------------------------------------------------
    @classmethod
    def ObjectReprImplBaseInitKwargs(cls) -> Dict[str, Any]:
        return {
            **{
                "allow_duplicate_names__": None,
            },
            **ScopedStatementTrait.ObjectReprImplBaseInitKwargs(),
        }

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _InitTraits(
        self,
        *,
        allow_duplicate_names: Optional[bool]=None,
        **kwargs,
    ) -> None:
        if allow_duplicate_names is not None:
            object.__setattr__(self, "allow_duplicate_names__", allow_duplicate_names)

        ScopedStatementTrait._InitTraits(self, **kwargs)
