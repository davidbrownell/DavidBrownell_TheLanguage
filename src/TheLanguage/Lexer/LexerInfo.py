# ----------------------------------------------------------------------
# |
# |  LexerInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-07 14:48:33
# |
# ----------------------------------------------------------------------
# | = """/*
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types and functions used to persist information used during the Lexer process"""

import os

from typing import Any, Callable, Optional, Tuple, Union

from dataclasses import (
    dataclass,
    fields,
    _PARAMS as DATACLASS_PARAMS,  # type: ignore
)

import CommonEnvironment
from CommonEnvironment import YamlRepr

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Location(YamlRepr.ObjectReprImplBase):
    Line: int
    Column: int

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Line >= 1, self
        assert self.Column >= 1, self


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class Region(YamlRepr.ObjectReprImplBase):
    Begin: Location
    End: Location

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.End.Line >= self.Begin.Line, self
        assert self.End.Line > self.Begin.Line or self.End.Column >= self.Begin.Column, self


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LexerData(YamlRepr.ObjectReprImplBase):

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        assert hasattr(self, DATACLASS_PARAMS) and not getattr(self, DATACLASS_PARAMS).repr, "Derived classes should be based on `dataclass` with `repr` set to `False`"
        YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LexerRegions(YamlRepr.ObjectReprImplBase):
    Self__: Region

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        assert hasattr(self, DATACLASS_PARAMS) and not getattr(self, DATACLASS_PARAMS).repr, "Derived classes should be based on `dataclass` with `repr` set to `False`"
        YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LexerInfo(YamlRepr.ObjectReprImplBase):
    Data: LexerData
    Regions: LexerRegions

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        valid_data_values = 0

        for field in fields(self.Data):
            valid_data_values += 1

            try:
                region_value = getattr(self.Regions, field.name)
            except AttributeError:
                assert False, field.name

            if getattr(self.Data, field.name) is None:
                assert region_value is None, field.name
            else:
                assert region_value is not None, field.name

        # The regions should have all of the data and a self field
        assert len(fields(self.Regions)) == valid_data_values + 1, (len(fields(self.Regions)), valid_data_values)

        YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)


# ----------------------------------------------------------------------
def SetLexerInfo(
    obj: Any,
    arg: Union[LexerInfo, Tuple[LexerData, LexerRegions]],
):
    if isinstance(arg, tuple):
        data, regions = arg

        # pylint: disable=too-many-function-args
        arg = LexerInfo(data, regions)

    object.__setattr__(obj, "Info", arg)


# ----------------------------------------------------------------------
def GetLexerInfo(
    obj: Any,
) -> LexerInfo:
    result = getattr(obj, "Info", None)

    # Eventually, everything will have Info. However, that isn't the case right now.
    # TODO: Remove this code ASAP
    if result is None:
        return LexerInfo(LexerData(), LexerRegions(Region(Location(1, 1), Location(1, 1))))
    # TODO: End

    assert result is not None, obj

    return result
