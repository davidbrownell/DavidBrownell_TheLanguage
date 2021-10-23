# ----------------------------------------------------------------------
# |
# |  ParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-28 17:13:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains utilities when working with parser-related information"""

import os

from typing import Any, Callable, Dict, List, Optional, Set, Union

from dataclasses import (
    dataclass,
    field,
    fields,
    InitVar,
    make_dataclass,
    _PARAMS as DATACLASS_PARAMS,  # type: ignore
)

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Location(object):
    Line: int
    Column: int

    # ----------------------------------------------------------------------
    def __post_init__(self):
        if self.Line != -1 or self.Column != -1:
            assert self.Line >= 1, self
            assert self.Column >= 1, self

    # ----------------------------------------------------------------------
    def __lt__(self, other):
        return self.Compare(self, other) < 0

    # ----------------------------------------------------------------------
    def __le__(self, other):
        return self.Compare(self, other) <= 0

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        return self.Compare(self, other) == 0

    # ----------------------------------------------------------------------
    def __ne__(self, other):
        return self.Compare(self, other) != 0

    # ----------------------------------------------------------------------
    def __gt__(self, other):
        return self.Compare(self, other) > 0

    # ----------------------------------------------------------------------
    def __ge__(self, other):
        return self.Compare(self, other) >= 0

    # ----------------------------------------------------------------------
    @staticmethod
    def Compare(
        left: "Location",
        right: "Location",
    ) -> int:
        delta = left.Line - right.Line
        if delta != 0:
            return delta

        delta = left.Column - right.Column
        if delta != 0:
            return delta

        return 0

    # ----------------------------------------------------------------------
    def ToString(self) -> str:
        return "[Ln {}, Col {}]".format(self.Line, self.Column)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Region(object):
    Begin: Location
    End: Location

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.End.Line >= self.Begin.Line, self
        assert self.End.Line > self.Begin.Line or self.End.Column >= self.Begin.Column, self

    # ----------------------------------------------------------------------
    def __contains__(self, other):
        return other.Begin >= self.Begin and other.End <= self.End

    # ----------------------------------------------------------------------
    def ToString(self) -> str:
        return "{} -> {}".format(self.Begin.ToString(), self.End.ToString())


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ParserInfo(Interface.Interface, YamlRepr.ObjectReprImplBase):

    regions: InitVar[List[Optional[Region]]]

    RegionsType__: Any                      = field(init=False, default=None)
    Regions__: Dict[str, Optional[Region]]  = field(init=False, default_factory=dict)

    _regionless_attributes: Set[str]        = field(init=False, default_factory=set)

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        regions: List[Optional[Region]],
        *,
        regionless_attributes: Optional[List[str]]=None,
        should_validate: Optional[bool]=True,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        assert hasattr(self, DATACLASS_PARAMS) and not getattr(self, DATACLASS_PARAMS).repr, "Derived classes should be based on `dataclass` with `repr` set to `False`"

        regionless_attributes_set = set(regionless_attributes or [])

        regionless_attributes_set.add("RegionsType__")
        regionless_attributes_set.add("Regions__")
        regionless_attributes_set.add("_regionless_attributes")

        object.__setattr__(self, "_regionless_attributes", regionless_attributes_set)

        cls_fields = fields(self)

        num_expected_fields = len(cls_fields) - len(self._regionless_attributes)
        assert len(regions) == num_expected_fields + 1, (len(regions), num_expected_fields + 1, "The number of regions provided must match the number of attributes that require them")

        # Populate the region values
        new_regions = {
            "Self__": regions[0],
        }

        next_regions_index = 1

        for the_field in cls_fields:
            if the_field.name in self._regionless_attributes: # pylint: disable=unsupported-membership-test
                continue

            new_regions[the_field.name] = regions[next_regions_index]
            next_regions_index += 1

        # Dynamically create the Regions class
        new_regions_class = make_dataclass(
            "{}Regions".format(self.__class__.__name__),
            [(k, Optional[Region]) for k in new_regions.keys()],
            bases=(YamlRepr.ObjectReprImplBase, ),
            frozen=True,
            repr=False,
        )

        # Create an instance of the new class
        new_regions_instance = new_regions_class(**new_regions)

        object.__setattr__(self, "RegionsType__", new_regions_class)
        object.__setattr__(self, "Regions__", new_regions_instance)

        YamlRepr.ObjectReprImplBase.__init__(
            self,
            RegionsType=None,
            _regionless_attributes=None,
            **custom_display_funcs,
        )

        if should_validate:
            self.Validate()

    # ----------------------------------------------------------------------
    def Validate(self):
        # ----------------------------------------------------------------------
        def IsOptional(the_field):
            if getattr(the_field.type, "__origin__", None) == Union:
                for arg in getattr(the_field.type, "__args__", []):
                    if arg == type(None):
                        return True

            return False

        # ----------------------------------------------------------------------

        for the_field in fields(self):
            data_value = getattr(self, the_field.name)

            if isinstance(data_value, list) and not data_value:
                assert data_value, (the_field.name, "Lists should never be empty; wrap it in 'Optional' if an empty list is a valid value")

            if the_field.name in self._regionless_attributes: # pylint: disable=unsupported-membership-test
                continue

            # The data and region values should both be None of both be not None
            region_value = getattr(self.Regions__, the_field.name)

            if data_value is None:
                assert IsOptional(the_field), (the_field.name, "The field definition should be 'Optional' when the value is None")
                assert region_value is None, (the_field.name, "The region value should be None when the data value is None")
            else:
                assert region_value is not None, (the_field.name, "The region value should not be None when the data value is not None")

        # Ensure that all regions fall within Self__
        for the_field in fields(self.Regions__):
            region_value = getattr(self.Regions__, the_field.name)
            if region_value is None:
                continue

            assert region_value in self.Regions__.Self__, (the_field.name, region_value, self.Regions__.Self__)  # type: ignore && pylint: disable=no-member

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def Accept(visitor, stack, *args, **kwargs):
        # TODO: Simplify accept by removing the concept of VisitType; Nodes are visitied before children and then can prevent recursion if they
        #       need different behavior.

        raise Exception("Abstract method")  # pragma: no cover
