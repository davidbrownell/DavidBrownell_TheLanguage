# ----------------------------------------------------------------------
# |
# |  TypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 08:28:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the TypeParserInfo object"""

import os

from typing import Any, Callable, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, Region

    from ..Common.MutabilityModifier import MutabilityModifier

    from ...Error import (  # pylint: disable=unused-import
        CreateError,
        Error,                              # Convenience import
        ErrorException,                     # Convenience import
    )


# ----------------------------------------------------------------------
MutabilityModifierRequiredError             = CreateError(
    "A mutability modifier is required in this context",
)

MutabilityModifierNotAllowedError           = CreateError(
    "A mutability modifier is not allowed in this context",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TypeParserInfo(ParserInfo):
    """Abstract base class for all types"""

    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    mutability_modifier: Optional[MutabilityModifier]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        regions,
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        super(TypeParserInfo, self).__init__(regions, regionless_attributes, validate, **custom_display_funcs)
