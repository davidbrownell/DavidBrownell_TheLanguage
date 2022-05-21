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
from typing import Any, Callable, Dict, List, Optional

from dataclasses import dataclass, field, InitVar

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.VisibilityModifier import VisibilityModifier
    from ..ParserInfo import ParserInfo, ParserInfoType, TranslationUnitRegion


# ----------------------------------------------------------------------
class ScopeFlag(Flag):
    """Indicates at which scope level(s) the statement is valid"""

    Root                                    = auto()
    Class                                   = auto()
    Function                                = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NamedStatementTrait(object):
    """Adds a name to the namespace"""

    # ----------------------------------------------------------------------
    name: str

    visibility_param: InitVar[VisibilityModifier]
    visibility: VisibilityModifier          = field(init=False)

    allow_name_to_be_duplicated__: bool     = field(init=False, default=False)

    # ----------------------------------------------------------------------
    def __post_init__(self, visibility_param):
        object.__setattr__(self, "visibility", visibility_param)

    # ----------------------------------------------------------------------
    @staticmethod
    def RegionlessAttributesArgs() -> List[str]:
        return [
            "allow_name_to_be_duplicated__",
        ]

    # ----------------------------------------------------------------------
    @staticmethod
    def ObjectReprImplBaseInitKwargs() -> Dict[str, Any]:
        return {
            "allow_name_to_be_duplicated__": None,
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
    ) -> None:
        if allow_name_to_be_duplicated is not None:
            object.__setattr__(self, "allow_name_to_be_duplicated__", allow_name_to_be_duplicated)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ScopedStatementTrait(NamedStatementTrait):
    """Add to a statement when it introduces a new scope"""
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NewNamespaceScopedStatementTrait(ScopedStatementTrait):
    """Add to statements to introducing new scoping rules"""

    # ----------------------------------------------------------------------
    allow_duplicate_names__: bool            = field(init=False, default=False)

    # ----------------------------------------------------------------------
    @classmethod
    def RegionlessAttributesArgs(cls) -> List[str]:
        return [
            "allow_duplicate_names__",
        ] + super(NewNamespaceScopedStatementTrait, cls).RegionlessAttributesArgs()

    # ----------------------------------------------------------------------
    @classmethod
    def ObjectReprImplBaseInitKwargs(cls) -> Dict[str, Any]:
        return {
            **{
                "allow_duplicate_names__": None,
            },
            **super(NewNamespaceScopedStatementTrait, cls).ObjectReprImplBaseInitKwargs(),
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

        super(NewNamespaceScopedStatementTrait, self)._InitTraits(**kwargs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class StatementParserInfo(ParserInfo):
    """Abstract base class for all statements"""

    # ----------------------------------------------------------------------
    scope_flags: ScopeFlag

    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

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
            scope_flags=None,                           # type: ignore
            **custom_display_funcs,
        )
