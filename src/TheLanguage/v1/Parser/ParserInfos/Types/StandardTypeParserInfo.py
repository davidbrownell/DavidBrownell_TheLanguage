# ----------------------------------------------------------------------
# |
# |  StandardTypeParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-12 10:46:35
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the StandardTypeParserInfo object"""

import os

from typing import List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .TypeParserInfo import ParserInfo, ParserInfoType, Region, TypeParserInfo

    from ..Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ..Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeItemParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    name: str

    templates: Optional[TemplateArgumentsParserInfo]
    constraints: Optional[ConstraintArgumentsParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(StandardTypeItemParserInfo, self).__init__(
            ParserInfoType.Unknown,
            *args,
            **kwargs,
            regionless_attributes=[
                "templates",
                "constraints",
            ],
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.templates:
            details.append(("templates", self.templates))
        if self.constraints:
            details.append(("constraints", self.constraints))

        return self._AcceptImpl(
            visitor,
            details=details,
            children=None,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StandardTypeParserInfo(TypeParserInfo):
    # ----------------------------------------------------------------------
    items: List[StandardTypeItemParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        *args,
        **kwargs,
    ):
        return cls(
            ParserInfoType.Unknown,         # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=[("items", self.items), ],  # type: ignore
            children=None,
        )
