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
import weakref

from contextlib import contextmanager
from enum import auto, Enum, Flag
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, TYPE_CHECKING

from dataclasses import dataclass, fields, make_dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Region import Region

    if TYPE_CHECKING:
        from ..NamespaceInfo import ParsedNamespaceInfo  # pylint: disable=unused-import


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
        return value != cls.Standard


# ----------------------------------------------------------------------
class ParserInfo(ObjectReprImplBase):
    """A collection of lexical tokens that may or may not be valid"""

    introduces_scope__                      = False

    # ----------------------------------------------------------------------
    def __init__(
        self,
        parser_info_type: ParserInfoType,
        regions: List[Optional[Region]],
        regionless_attributes: Optional[List[str]]=None,
        validate=True,
        **custom_display_funcs: Callable[[Any], Optional[Any]],
    ):
        object.__setattr__(self, "_parser_info_type", parser_info_type)
        object.__setattr__(self, "_disabled", False)

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

        # Assign the region info to this instance
        object.__setattr__(self, "_RegionsType", new_regions_class)
        object.__setattr__(self, "_regions", new_regions_instance)

        regionless_attributes_set.add("_RegionsType")
        regionless_attributes_set.add("_regions")
        regionless_attributes_set.add("_validate_regions_func")

        # Create the dynamic validate func
        object.__setattr__(
            self,
            "_validate_regions_func",
            ParserInfo._ValidateRegionsFuncFactory(self, all_fields, regionless_attributes_set),
        )

        ObjectReprImplBase.__init__(
            self,
            introduces_scope__=None,
            parser_info_type__=None,
            is_disabled__=None,
            namespace__=None,
            is_namespace__initialized__=None,
            **custom_display_funcs,
        )

        # Validate the instance
        if validate:
            self.ValidateRegions()

    # ----------------------------------------------------------------------
    @property
    def RegionsType__(self) -> Any:
        return self._RegionsType  # type: ignore  # pylint: disable=no-member

    @property
    def regions__(self) -> Any:
        return self._regions  # type: ignore  # pylint: disable=no-member

    @property
    def parser_info_type__(self) -> ParserInfoType:
        return self._parser_info_type  # type: ignore  # pylint: disable=no-member

    @property
    def is_disabled__(self) -> bool:
        return self._disabled  # type: ignore  # pylint: disable=no-member

    # ----------------------------------------------------------------------
    def ValidateRegions(self) -> None:
        self._validate_regions_func()  # type: ignore  # pylint: disable=no-member

    # ----------------------------------------------------------------------
    def Disable(self) -> None:
        object.__setattr__(self, "_disabled", True)

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def Accept(self, visitor):
        if self.is_disabled__:
            return VisitResult.SkipAll

        with self._GenericAccept(visitor) as visit_result:
            if visit_result == VisitResult.SkipAll:
                return

            method_name = "On{}".format(self.__class__.__name__)

            method = getattr(visitor, method_name, None)
            assert method is not None, method_name

            with method(self):
                pass

    # ----------------------------------------------------------------------
    @Interface.extensionmethod
    def GetNameAndRegion(self) -> Tuple[Optional[str], Region]:
        if hasattr(self, "name"):
            return self.name, self.regions__.name  # type: ignore  # pylint: disable=no-member

        return None, self.regions__.self__

    # ----------------------------------------------------------------------
    # This method is invoked during validation
    def InitNamespace(
        self,
        value: "ParsedNamespaceInfo",
    ) -> None:
        assert not self.is_namespace__initialized__
        object.__setattr__(self, self.__class__._NAMESPACE_ATTRIBUTE_NAME, weakref.ref(value))  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    @property
    def namespace__(self) -> "ParsedNamespaceInfo":
        return getattr(self, self.__class__._NAMESPACE_ATTRIBUTE_NAME)()  # pylint: disable=protected-access

    @property
    def is_namespace__initialized__(self) -> bool:
        return hasattr(self, self.__class__._NAMESPACE_ATTRIBUTE_NAME)  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _AcceptImpl(
        self,
        visitor,
        details: Optional[
            List[
                Tuple[
                    str,
                    Union[
                        "ParserInfo",
                        List["ParserInfo"],
                    ],
                ],
            ]
        ],
        children: Optional[List["ParserInfo"]],
    ):
        """Implementation of Accept for ParserInfos that introduce new scopes or contain details that should be enumerated"""

        if self.is_disabled__:
            return VisitResult.SkipAll

        with self._GenericAccept(visitor) as visit_result:
            if visit_result == VisitResult.SkipAll:
                return

            method_name = "On{}".format(self.__class__.__name__)

            method = getattr(visitor, method_name, None)
            assert method is not None, method_name

            try:
                with method(self) as visit_result:
                    if visit_result is None:
                        visit_result = VisitResult.Continue

                    if details and not visit_result & VisitResult.SkipDetails:
                        method_name_prefix = "On{}__".format(self.__class__.__name__)

                        for detail_name, detail_value in details:
                            method_name = "{}{}".format(method_name_prefix, detail_name)

                            method = getattr(visitor, method_name, None)
                            assert method is not None, method_name

                            method(detail_value)

                    if children:
                        assert (
                            self.introduces_scope__
                            or all(child.introduces_scope__ for child in children)
                        )

                        if not visit_result & VisitResult.SkipChildren:
                            for child in children:
                                child.Accept(visitor)

            except AttributeError as ex:
                if str(ex) == "__enter__":
                    assert False, (method_name, "__enter__")

                raise

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _NAMESPACE_ATTRIBUTE_NAME               = "_namespace"

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
    @contextmanager
    def _GenericAccept(self, visitor):
        method_name = "OnPhrase"
        method = getattr(visitor, method_name, None)

        if method is None:
            yield
            return

        with method(self) as visit_result:
            yield visit_result


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class RootParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    introduces_scope__                      = True

    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[Region]]]

    statements: Optional[List[ParserInfo]]
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
        super(RootParserInfo, self).__init__(ParserInfoType.Standard, regions)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        return self._AcceptImpl(
            visitor,
            details=None,
            children=self.statements,
        )
