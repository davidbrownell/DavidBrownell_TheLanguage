# ----------------------------------------------------------------------
# |
# |  TupleTypeParserInfo.py
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
"""Contains the TupleTypeParserInfo object"""

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
    from .TypeParserInfo import (
        Error,
        ErrorException,
        MutabilityModifierRequiredError,
        TypeParserInfo,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TupleTypeParserInfo(TypeParserInfo):
    types: List[TypeParserInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(TupleTypeParserInfo, self).__post_init__(regions)

        # Validate
        errors: List[Error] = []

        for contained_type in self.types:
            if contained_type.mutability_modifier is None:
                errors.append(
                    MutabilityModifierRequiredError.Create(
                        region=contained_type.regions__.self__,
                    ),
                )

        if errors:
            raise ErrorException(*errors)
