# ----------------------------------------------------------------------
# |
# |  Phrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 09:41:42
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the Phrase object"""

import os

from enum import auto, Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from dataclasses import dataclass, fields, make_dataclass, InitVar

import CommonEnvironment
from CommonEnvironment.CallOnExit import CallOnExit
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.Region import Region


# ----------------------------------------------------------------------
class VisitControl(Enum):
    """Controls visitation behavior"""

    Continue                                = auto()    # Continue visiting all children
    SkipChildren                            = auto()    # Don't visit any children
    SkipSiblings                            = auto()    # Don't visit any remaining siblings
    Terminate                               = auto()    # Don't visit anything else


# ----------------------------------------------------------------------
class Phrase(ObjectReprImplBase):
    """A collection of lexical tokens that may or may not be valid"""

    has_children__                          = False

    # ----------------------------------------------------------------------
    def __init__(
        self,
        regions: List[Optional[Region]],
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        regionless_attributes_set = set(regionless_attributes or [])

        # Dynamically create the Regions type based on the fields of the class
        all_fields = {f.name : f for f in fields(self)}

        num_expected_regions = len(all_fields) - len(regionless_attributes_set)
        assert len(regions) == num_expected_regions + 1, (len(regions), num_expected_regions + 1, "The number of regions provided must match the number of attributes that require them")

        # Populate the regions
        new_regions = {
            "self__" : regions[0],
        }

        next_regions_index = 1

        for attribute in all_fields.keys():
            if attribute in regionless_attributes_set:
                continue

            new_regions[attribute] = regions[next_regions_index]
            next_regions_index += 1

        # Create the class
        new_regions_class = make_dataclass(
            "{}Regions".format(self.__class__.__name__),
            [(k, Optional[Region]) for k in new_regions.keys()],  # type: ignore
            bases=(ObjectReprImplBase,),
            frozen=True,
            repr=False,
        )

        # Create an instance of the new class
        new_regions_instance = new_regions_class(**new_regions)

        # When displaying content for the regions class, omit values where the region is None
        # (don't display 'None' inline, just don't show them)
        ObjectReprImplBase.__init__(new_regions_instance, **{k:None for k, v in new_regions_instance.__dict__.items() if v is None})

        # Assign the region info to this phrase instance
        object.__setattr__(self, "_RegionsType", new_regions_class)
        object.__setattr__(self, "_regions", new_regions_instance)

        regionless_attributes_set.add("_RegionsType")
        regionless_attributes_set.add("_regions")
        regionless_attributes_set.add("_validate_regions_func")

        # Create the dynamic validate func
        object.__setattr__(
            self,
            "_validate_regions_func",
            Phrase._ValidateRegionsFuncFactory(self, all_fields, regionless_attributes_set),
        )

        ObjectReprImplBase.__init__(
            self,
            has_children__=None,
            **custom_display_funcs,
        )

        # Validate the phrase
        if validate:
            self.ValidateRegions()

    # ----------------------------------------------------------------------
    @property
    def RegionsType__(self) -> Any:
        return self._RegionsType  # type: ignore # <Has no member> pylint: disable=E1101

    @property
    def regions__(self) -> Any:
        return self._regions  # type: ignore # <Has no member> pylint: disable=E1101

    # ----------------------------------------------------------------------
    def ValidateRegions(self) -> None:
        self._validate_regions_func()  # type: ignore # <Has no member> pylint: disable=E1101

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def Accept(self, visitor) -> VisitControl:
        on_method = getattr(visitor, "On{}".format(self.__class__.__name__), None)
        assert on_method is not None

        visit_control = on_method(self)

        if visit_control is None:
            visit_control = VisitControl.Continue
        elif visit_control in [VisitControl.SkipChildren, VisitControl.SkipSiblings]:
            visit_control = VisitControl.Continue

        return visit_control

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _ScopedAcceptImpl(
        self,
        children: List["Phrase"],
        visitor,
    ) -> VisitControl:
        """Implementation of Accept for phrases that introduce new scopes"""

        # Get the visitor's dynamic methods
        enter_method = getattr(visitor, "OnEnter{}".format(self.__class__.__name__), None)
        assert enter_method is not None

        exit_method = getattr(visitor, "OnExit{}".format(self.__class__.__name__), None)
        assert exit_method is not None

        # Invoke the visitor
        visit_control = enter_method(self)
        if visit_control is None:
            visit_control = VisitControl.Continue

        if visit_control != VisitControl.Terminate:
            with CallOnExit(lambda: exit_method(self)):
                if visit_control == VisitControl.SkipChildren:
                    visit_control = VisitControl.Continue
                else:
                    visitor.OnEnterScope(self)
                    with CallOnExit(lambda: visitor.OnExitScope(self)):
                        for child in children:
                            visit_control = child.Accept(visitor)
                            if visit_control is None:
                                visit_control = VisitControl.Continue

                            if visit_control == VisitControl.Continue:
                                pass # Nothing to do here
                            elif visit_control == VisitControl.Terminate:
                                break
                            elif visit_control == VisitControl.SkipSiblings:
                                visit_control = VisitControl.Continue
                                break
                            else:
                                assert False, visit_control  # pragma: no cover

        assert visit_control in [VisitControl.Continue, VisitControl.Terminate], visit_control
        return visit_control

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    def _ValidateRegionsFuncFactory(
        phrase: "Phrase",
        all_fields: Dict[str, Any],
        regionless_attributes_set: Set[str],
    ) -> Callable[[], None]:
        # ----------------------------------------------------------------------
        def Func():
            # Ensure that the regions in the new instance are valid based on the state of the phrase

            # ----------------------------------------------------------------------
            def IsOptional(
                attribute_name: str,
            ) -> bool:
                the_field = all_fields[attribute_name]

                if getattr(the_field.type, "__origin__", None) == Union:
                    for arg in getattr(the_field.type, "__args__", []):
                        if arg == type(None):
                            return True

                return False

            # ----------------------------------------------------------------------

            for attribute_name in all_fields.keys():
                if attribute_name in regionless_attributes_set:
                    continue

                attribute_value = getattr(phrase, attribute_name)

                assert not isinstance(attribute_value, list) or attribute_value, "Lists should never be empty"

                region_value = getattr(phrase.regions__, attribute_name)  # type: ignore

                if attribute_value is None:
                    assert IsOptional(attribute_name), (attribute_name, "The field definition should be 'Optional' when the value is None")
                    assert region_value is None, (attribute_name, "The region value should be None when the data value is None")
                else:
                    assert region_value is not None, (attribute_name, "The region value should not be None when the data value is not None")

                    # Ensure that the region value falls within self__
                    assert region_value in phrase.regions__.self__, (attribute_name, region_value, phrase.regions__.self__)  # type: ignore

        # ----------------------------------------------------------------------

        return Func


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class RootPhrase(Phrase):
    has_children__                          = True

    regions: InitVar[List[Optional[Region]]]
    statements: Optional[List[Phrase]]
    documentation: Optional[str]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, regions):
        super(RootPhrase, self).__init__(regions)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, *args, **kwargs):
        return self._ScopedAcceptImpl(self.statements or [], *args, **kwargs)
