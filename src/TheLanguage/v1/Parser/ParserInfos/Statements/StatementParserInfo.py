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
from typing import Any, Callable, Dict, Generator, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..ParserInfo import ParserInfo, ParserInfoType, TranslationUnitRegion

    # Convenience imports
    from ..ParserInfo import CompileTimeInfo            # pylint: disable=unused-import


# ----------------------------------------------------------------------
class ScopeFlag(Flag):
    """Indicates at which scope level(s) the statement is valid"""

    Root                                    = auto()
    Class                                   = auto()
    Function                                = auto()

    # This value should never be used directly
    Empty                                   = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StatementParserInfo(ParserInfo):
    """Abstract base class for all statements"""

    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        parser_info_type,
        regions,
        *,
        regionless_attributes: Optional[List[str]]=None,
        finalize=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        assert parser_info_type != ParserInfoType.Unknown

        super(StatementParserInfo, self).__init__(
            parser_info_type,
            regions,
            **{
                **custom_display_funcs,
                **{
                    "regionless_attributes": regionless_attributes or [],
                    "finalize": finalize,
                },
            },
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def GetValidScopes() -> Dict[ParserInfoType, ScopeFlag]:
        """Returns the scopes in which the statement can be considered valid"""
        raise Exception("Abstract method")  # pragma: no cover
