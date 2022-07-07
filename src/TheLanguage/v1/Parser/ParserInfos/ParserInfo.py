# ----------------------------------------------------------------------
# |
# |  ParserInfo.py
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
"""Contains the ParserInfo object"""

import os

from contextlib import contextmanager
from enum import auto, Enum, Flag
from typing import Any, Callable, Dict, Generator, List, Optional, Set, Tuple, Union

from dataclasses import dataclass, fields, make_dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .ParserInfoVisitorHelper import ParserInfoVisitorHelper

    from ..TranslationUnitRegion import TranslationUnitRegion
    from ..MiniLanguage.Types.Type import Type as MiniLanguageType


# ----------------------------------------------------------------------
class VisitResult(Flag):
    Continue                                = 0

    SkipDetails                             = auto()
    SkipChildren                            = auto()

    SkipAll                                 = SkipDetails | SkipChildren


# ----------------------------------------------------------------------
class ParserInfoType(Enum):
    Unknown                                 = auto()    # Unknown (this value should only be applied for very low-level phrases (like types))

    # Compile-Time Flags
    CompileTimeTemporary                    = auto()    # Indicates that the ParserInfo is applicable at compile-time, but it isn't clear if this means Configuration or TypeCustomization.
                                                        #     Parent types should override this value when additional context is understood.

    Configuration                           = auto()    # Can be used in the specification of basic compile-time types
    TypeCustomization                       = auto()    # Can be used in the evaluation of compile-time constraints

    # Standard Flags
    Standard                                = auto()

    # ----------------------------------------------------------------------
    @classmethod
    def GetDominantType(
        cls,
        *expressions: "ParserInfo",
    ) -> "ParserInfoType":
        dominant_expression: Optional["ParserInfo"] = None

        for expression in expressions:
            expression_value = expression.parser_info_type__

            if (
                dominant_expression is None
                or expression_value.value > dominant_expression.parser_info_type__.value
            ):
                dominant_expression = expression

        return dominant_expression.parser_info_type__ if dominant_expression else cls.Unknown

    # ----------------------------------------------------------------------
    @classmethod
    def IsConfiguration(
        cls,
        value: "ParserInfoType",
    ) -> bool:
        return value == cls.Configuration or value == cls.Unknown

    # ----------------------------------------------------------------------
    @classmethod
    def IsCompileTime(
        cls,
        value: "ParserInfoType",
    ) -> bool:
        return value != cls.Standard and value != cls.Unknown


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class CompileTimeInfo(object):
    type: MiniLanguageType
    value: Any


# ----------------------------------------------------------------------
class ParserInfo(Interface.Interface, ObjectReprImplBase):
    """A collection of lexical tokens that may or may not be valid"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info_type: ParserInfoType,
        regions: List[Optional[TranslationUnitRegion]],
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        object.__setattr__(self, "_disabled", False)
        object.__setattr__(self, "_parser_info_type", parser_info_type)
        object.__setattr__(self, "_parent_name", None)

        regionless_attributes_set = set(regionless_attributes or [])

        # Dynamically create the Regions type based on the fields of the class
        all_fields = {f.name : f for f in fields(self) if not f.name.startswith("_")}

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
            [(k, Optional[TranslationUnitRegion]) for k in new_regions.keys()],  # type: ignore
            bases=(ObjectReprImplBase,),
            frozen=True,
            repr=False,
        )

        # Create an instance of the new class
        new_regions_instance = new_regions_class(**new_regions)

        # When displaying content for the regions class, omit values where the region is None
        # (don't display 'None' inline, just don't show them)
        ObjectReprImplBase.__init__(new_regions_instance, **{k:None for k, v in new_regions_instance.__dict__.items() if v is None})

        # Assign the region info to this instance
        object.__setattr__(self, "_RegionsType", new_regions_class)
        object.__setattr__(self, "_regions", new_regions_instance)

        # Create the dynamic validate func
        object.__setattr__(
            self,
            "_validate_regions_func",
            ParserInfo._ValidateRegionsFuncFactory(self, all_fields, regionless_attributes_set),
        )

        ObjectReprImplBase.__init__(
            self,
            **{
                **{
                    "is_compile_time__": None,
                    "is_disabled__": None,
                    "parent_name__": None,
                    "parser_info_type__": None,
                },
                **custom_display_funcs,
            },
        )

        # Validate the instance
        if validate:
            self.ValidateRegions()

    # ----------------------------------------------------------------------
    @property
    def is_compile_time__(self) -> bool:
        return ParserInfoType.IsCompileTime(self.parser_info_type__)

    @property
    def is_disabled__(self) -> bool:
        return self._disabled  # type: ignore  # pylint: disable=no-member

    @property
    def parent_name__(self) -> List[str]:
        assert self._parent_name is not None  # type: ignore  # pylint: disable=no-member
        return self._parent_name              # type: ignore  # pylint: disable=no-member

    @property
    def parser_info_type__(self) -> ParserInfoType:
        return self._parser_info_type  # type: ignore  # pylint: disable=no-member

    @property
    def RegionsType__(self) -> Any:
        return self._RegionsType  # type: ignore  # pylint: disable=no-member

    @property
    def regions__(self) -> Any:
        return self._regions  # type: ignore  # pylint: disable=no-member

    # ----------------------------------------------------------------------
    def ValidateRegions(self) -> None:
        self._validate_regions_func()  # type: ignore  # pylint: disable=no-member

    # ----------------------------------------------------------------------
    def Disable(self) -> None:
        assert self.is_disabled__ is False
        object.__setattr__(self, "_disabled", True)

    # ----------------------------------------------------------------------
    def OverrideParserInfoType(
        self,
        new_parser_info_type: ParserInfoType,
    ) -> None:
        if self.parser_info_type__ == ParserInfoType.Unknown:
            # Literals are the only things that can be created as Unknown, so no
            # need to recurse.
            object.__setattr__(self, "_parser_info_type", new_parser_info_type)
            return

        # ----------------------------------------------------------------------
        class Visitor(ParserInfoVisitorHelper):
            # ----------------------------------------------------------------------
            @staticmethod
            @contextmanager
            def OnPhrase(
                parser_info: ParserInfo,
            ):
                if parser_info.parser_info_type__ == ParserInfoType.CompileTimeTemporary:
                    object.__setattr__(parser_info, "_parser_info_type", new_parser_info_type)

                yield

        # ----------------------------------------------------------------------

        self.Accept(Visitor())

    # ----------------------------------------------------------------------
    def Accept(
        self,
        visitor,
        *,
        include_disabled=False,
    ):
        if self.is_disabled__ and not include_disabled:
            return VisitResult.SkipAll

        method = getattr(visitor, "OnPhrase", None) or self.__class__._GenericAcceptGenerator  # pylint: disable=protected-access
        with method(self) as visit_result:
            if visit_result == VisitResult.SkipAll:
                return

            method_name = "On{}".format(self.__class__.__name__)

            method = getattr(visitor, method_name, None)
            assert method is not None, method_name

            with method(self) as visit_result:
                if visit_result is None:
                    visit_result = VisitResult.Continue

                if not visit_result & VisitResult.SkipDetails:
                    all_accept_details = list(self._GenerateAcceptDetails())

                    if all_accept_details:
                        method = getattr(visitor, "OnPhraseDetails", None) or self.__class__._GenericAcceptGenerator  # pylint: disable=protected-access
                        with method(self) as details_visit_result:
                            if details_visit_result is None:
                                details_visit_result = VisitResult.Continue

                            if (
                                not details_visit_result & VisitResult.SkipAll
                                and not details_visit_result & VisitResult.SkipDetails
                            ):
                                method_name_prefix = "On{}__".format(self.__class__.__name__)

                                for detail_name, detail_value in all_accept_details:
                                    method_name = "{}{}".format(method_name_prefix, detail_name)

                                    method = getattr(visitor, method_name, None)
                                    assert method is not None, method_name

                                    method(
                                        detail_value,
                                        include_disabled=include_disabled,
                                    )

                if not visit_result & VisitResult.SkipChildren:
                    all_children = list(self._GenerateAcceptChildren())

                    if all_children:
                        method = getattr(visitor, "OnPhraseChildren", None) or self.__class__._GenericAcceptGenerator  # pylint: disable=protected-access
                        with method(self) as children_visit_result:
                            if children_visit_result is None:
                                children_visit_result = VisitResult.Continue

                            if (
                                not children_visit_result & VisitResult.SkipAll
                                and not children_visit_result & VisitResult.SkipChildren
                            ):
                                for child in self._GenerateAcceptChildren():
                                    child.Accept(
                                        visitor,
                                        include_disabled=include_disabled,
                                    )

    # ----------------------------------------------------------------------
    @contextmanager
    def InitConfiguration(
        self,
        names: List[str],
        configuration_info: Dict[str, CompileTimeInfo],
    ):
        """Opportunity for a ParserInfo object to initialize itself during the configuration process."""

        assert self._parent_name is None  # type: ignore  # pylint: disable=no-member
        object.__setattr__(self, "_parent_name", names)

        if self.parser_info_type__ == ParserInfoType.Configuration:
            with self._InitConfigurationImpl(configuration_info) as visit_result:
                yield visit_result
        else:
            yield

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def Lower(self) -> Optional["ParserInfo"]:
        """\
        Opportunity for a ParserInfo object to return a simplified version of itself.

        Lowering is helpful in that it provides a robust collection of ParserInfo objects to make
        parsing more natural, but a reducing layer to ensure that other components don't need
        knowledge of a broad set of ParserInfo objects.
        """

        # By default, no lowering
        return None

    # ----------------------------------------------------------------------
    # |
    # |  Protected Types
    # |
    # ----------------------------------------------------------------------
    _GenerateAcceptDetailsResultType        = Generator[
        Tuple[str, Union["ParserInfo", List["ParserInfo"]]],
        None,
        None,
    ]

    # ----------------------------------------------------------------------
    _GenerateAcceptChildrenResultType       = Generator[
        "ParserInfo",
        None,
        None,
    ]

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def _GenerateAcceptDetails(self) -> "ParserInfo._GenerateAcceptDetailsResultType":
        # Nothing by default
        if False:
            yield

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def _GenerateAcceptChildren(self) -> "ParserInfo._GenerateAcceptChildrenResultType":
        # No children by default
        if False:
            yield

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    def _ValidateRegionsFuncFactory(
        parser_info: "ParserInfo",
        all_fields: Dict[str, Any],
        regionless_attributes_set: Set[str],
    ) -> Callable[[], None]:
        # ----------------------------------------------------------------------
        def Func():
            # Ensure that the regions in the new instance are valid based on the state of the ParserInfo

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

                attribute_value = getattr(parser_info, attribute_name)

                assert not isinstance(attribute_value, list) or attribute_value, "Lists should never be empty"

                region_value = getattr(parser_info.regions__, attribute_name)  # type: ignore

                if attribute_value is None:
                    assert IsOptional(attribute_name), (attribute_name, "The field definition should be 'Optional' when the value is None")
                    assert region_value is None, (attribute_name, "The region value should be None when the data value is None")
                else:
                    assert region_value is not None, (attribute_name, "The region value should not be None when the data value is not None")

                    # Ensure that the region value falls within self__
                    assert region_value in parser_info.regions__.self__, (attribute_name, region_value, parser_info.regions__.self__)  # type: ignore

        # ----------------------------------------------------------------------

        return Func

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def _GenericAcceptGenerator(*args, **kwargs):  # pylint: disable=unused-argument
        yield VisitResult.Continue

    # ----------------------------------------------------------------------
    @classmethod
    @contextmanager
    @Interface.extensionmethod
    def _InitConfigurationImpl(
        cls,
        configuration_data: Dict[str, CompileTimeInfo], # pylint: disable=unused-argument
    ):
        raise Exception("This functionality should be implemented by derived classes when applicable ({})".format(cls))
