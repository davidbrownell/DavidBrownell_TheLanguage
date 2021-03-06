# ----------------------------------------------------------------------
# |
# |  StatementParserInfo.py
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
"""Contains the StatementParserInfo object"""

import os

from enum import auto, Flag
from typing import Any, Callable, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, ParserInfoType, Region


# ----------------------------------------------------------------------
class ScopeFlag(Flag):
    """Indicates at which scope level(s) the statement is valid"""

    Root                                    = auto()
    Class                                   = auto()
    Function                                = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StatementParserInfo(ParserInfo):
    """Abstract base class for all statements"""

    # ----------------------------------------------------------------------
    allow_duplicate_named_items__           = False

    # ----------------------------------------------------------------------
    scope_flags: ScopeFlag

    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[Region]]]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        parser_info_type,
        regions,
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        assert parser_info_type != ParserInfoType.Unknown

        super(StatementParserInfo, self).__init__(
            parser_info_type,
            regions,
            (regionless_attributes or []) + ["scope_flags", ],
            validate,
            allow_duplicate_named_items__=None,         # type: ignore
            scope_flags=None,                           # type: ignore
            **custom_display_funcs,
        )
