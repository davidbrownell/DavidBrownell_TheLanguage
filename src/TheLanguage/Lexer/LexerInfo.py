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

from typing import Any, Callable, List, Optional, Set, Union

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

        for field in fields(self):
            if field.init:
                self._ValidateImpl(field)

        YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)

    # ----------------------------------------------------------------------
    def Validate(self):
        """Validates all fields that are to be populated after the object is constructed"""

        for field in fields(self):
            if not field.init:
                self._ValidateImpl(field)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _ValidateImpl(self, field):
        field_type = getattr(field.type, "__origin__", None)

        # Lists should never be empty
        if field_type == List:
            data_value = getattr(self, field.name)
            assert data_value, (field.name, "Lists should never be empty; wrap it in 'Optional' if an empty list is a valid value")


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
        should_validate=True,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        if should_validate:
            self.Validate(
                # No need to validate data, as it will have already been validated
                # during construction.
                validate_data=False,
            )

        YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)

    # ----------------------------------------------------------------------
    def Validate(
        self,
        attributes_to_skip: Optional[Set[str]]=None,
        validate_data=True,
    ):
        if attributes_to_skip is None:
            attributes_to_skip = set()

        # ----------------------------------------------------------------------
        def IsOptional(field):
            if getattr(field.type, "__origin__", None) != Union:
                return False

            for arg in getattr(field.type, "__args__", []):
                if arg == type(None):
                    return True

            return False

        # ----------------------------------------------------------------------

        region_fields = {field.name : field for field in fields(self.Regions)}

        valid_data_values = 0

        for field in fields(self.Data):
            if field.name in attributes_to_skip:
                continue

            valid_data_values += 1

            region_field = region_fields.get(field.name, None)
            assert region_field is not None, (field.name, "This value is not defined in Regions")

            # The data field should be optional if the region field is optional
            assert IsOptional(region_field) == IsOptional(field), (field.name, "Data fields should be Optional if region fields are Optional")

            # The data and region values should match in that they are either both None or both
            # not None
            region_value = getattr(self.Regions, field.name)

            if getattr(self.Data, field.name) is None:
                assert region_value is None, field.name
            else:
                assert region_value is not None, field.name

        # The regions should have all of the data and a self field
        assert len(fields(self.Regions)) == valid_data_values + 1, (len(fields(self.Regions)), valid_data_values)

        if validate_data:
            self.Data.Validate()


# ----------------------------------------------------------------------
def SetLexerInfo(
    obj: Any,
    arg: LexerInfo,
):
    object.__setattr__(obj, "Info", arg)


# ----------------------------------------------------------------------
def GetLexerInfo(
    obj: Any,
) -> LexerInfo:
    result = getattr(obj, "Info", None)

    # TODO: Eventually, everything will have Info. However, that isn't the case right now.
    # TODO: Remove this code ASAP
    if result is None:
        # pylint: disable=too-many-function-args
        return LexerInfo(LexerData(), LexerRegions(Region(Location(1, 1), Location(1, 1))))
    # TODO: End

    assert result is not None, obj

    return result
