# ----------------------------------------------------------------------
# |
# |  LiteralParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-22 10:13:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the LiteralParserInfo object"""

import os

from typing import Type

from dataclasses import dataclass, fields

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LiteralParserInfo(ParserInfo):
    """Abstract base class for all literal parser info objects"""

    Value: Type[None]                       # To be overridden by derived class

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(LiteralParserInfo, self).__post_init__(
            regions,
            regionless_attributes=["Value"],
        )

        # Ensure that value is not Type[None]
        these_fields = [field for field in fields(self) if not (field.name.startswith("_") or field.name.endswith("_"))]
        assert len(these_fields) == 1, "Only one field should be defined"
        assert these_fields[0].name == "Value", "Value should be the only field"
