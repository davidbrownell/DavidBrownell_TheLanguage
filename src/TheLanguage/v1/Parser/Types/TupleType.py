# ----------------------------------------------------------------------
# |
# |  TupleType.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 09:02:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TupleType object"""

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
    from .TypePhrase import MutabilityModifierRequiredError, TypePhrase


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleType(TypePhrase):
    types: List[TypePhrase]

    # ----------------------------------------------------------------------
    def __post_init__(self, diagnostics, regions):
        super(TupleType, self).__post_init__(diagnostics, regions)

        # Validate
        for contained_type in self.types:
            if contained_type.mutability_modifier is None:
                diagnostics.errors.append(
                    MutabilityModifierRequiredError.Create(
                        region=contained_type.regions__.self__,
                    ),
                )
