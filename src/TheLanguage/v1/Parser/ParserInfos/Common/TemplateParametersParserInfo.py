# ----------------------------------------------------------------------
# |
# |  TemplateParametersParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-13 17:41:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about template parameters"""

import itertools
import os

from typing import Any, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.VisibilityModifier import VisibilityModifier

    from ..Expressions.ExpressionParserInfo import (
        ExpressionParserInfo,
        ParserInfo,
        ParserInfoType,
        TranslationUnitRegion,
    )

    from ..Expressions.Traits.SimpleExpressionTrait import SimpleExpressionTrait

    from ..Traits.NamedTrait import NamedTrait

    from ...Error import CreateError, Error, ErrorException

    from ...Common import CallHelpers
    from ...Common import MiniLanguageHelpers


# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The template parameter '{name}' has already been defined",
    name=str,
    prev_region=TranslationUnitRegion,
)

DuplicateVariadicError                      = CreateError(
    "A variadic template parameter has already been defined",
    prev_region=TranslationUnitRegion,
)

InvalidTemplateDecoratorTypeError           = CreateError(
    "Template decorator parameters must be compile-time types",
)

InvalidTemplateDecoratorExpressionError     = CreateError(
    "Template decorator parameters must be compile-time expressions",
)

InvalidTypeError                            = CreateError(
    "Invalid template decorator value; '{expected_type}' expected but '{actual_type}' was found",
    expected_type=str,
    expected_region=TranslationUnitRegion,
    actual_type=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateTypeParameterParserInfo(
    NamedTrait,
    ParserInfo,
):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    is_variadic: Optional[bool]
    default_type: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[TranslationUnitRegion]],
        name: str,
        *args,
        **kwargs,
    ):
        # We are automatically setting the visibility, so add a region as well
        regions.insert(0, regions[0])

        return cls(
            name,
            VisibilityModifier.private,     # type: ignore
            regions,                        # type: ignore
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(
        self,
        visibility_param,
        regions,
    ):
        ParserInfo.__init__(
            self,
            ParserInfoType.TypeCustomization,
            regions,
            **{
                **NamedTrait.ObjectReprImplBaseInitKwargs(),
                **{
                    "regionless_attributes": [
                        "default_type",
                    ]
                        + NamedTrait.RegionlessAttributesArgs()
                    ,
                    "finalize": False,
                },
            },
        )

        NamedTrait.__post_init__(self, visibility_param)

        self._Finalize()

        # Validate
        errors: List[Error] = []

        if self.default_type:
            try:
                self.default_type.InitializeAsType(self.parser_info_type__)

                # The expression itself might be a type or an expression that yields a type, so
                # we can't make assumptions about the actual type until it is resolved.

            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def IsNameOrdered(*args, **kwargs) -> bool:  # pylint: disable=unused-argument
        return True

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        if self.default_type is not None:
            yield "default_type", self.default_type  # type: ignore

    # ----------------------------------------------------------------------
    @Interface.override
    def _GetUniqueId(self) -> Tuple[Any, ...]:
        assert self.default_type is None
        return (None, )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateDecoratorParameterParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    type: ExpressionParserInfo
    name: str
    default_value: Optional[ExpressionParserInfo]

    is_simple_expression__: bool            = field(init=False, default=False)

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
        super(TemplateDecoratorParameterParserInfo, self).__init__(
            ParserInfoType.TypeCustomization,
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "type",
                        "default_value",
                        "is_simple_expression__",
                    ],
                    "is_simple_expression__": None,
                },
            },
        )

        is_simple_type = isinstance(self.type, SimpleExpressionTrait)
        is_simple_default = isinstance(self.default_value, SimpleExpressionTrait)

        object.__setattr__(
            self,
            "is_simple_expression__",
            is_simple_type and (self.default_value is None or is_simple_default),
        )

        # Validate
        errors: List[Error] = []

        try:
            if self.type.parser_info_type__ != ParserInfoType.TypeCustomization:
                errors.append(
                    InvalidTemplateDecoratorTypeError.Create(
                        region=self.type.regions__.self__,
                    ),
                )

            self.type.InitializeAsType(ParserInfoType.TypeCustomization)

        except ErrorException as ex:
            errors += ex.errors

        if self.default_value is not None:
            try:
                self.default_value.InitializeAsExpression()

                if (
                    not self.default_value.is_compile_time__
                    and self.default_value.parser_info_type__ != ParserInfoType.Unknown
                ):
                    errors.append(
                        InvalidTemplateDecoratorExpressionError.Create(
                            region=self.default_value.regions__.self__,
                        ),
                    )

            except ErrorException as ex:
                errors += ex.errors

        if (
            not errors
            and is_simple_type
            and is_simple_default
        ):
            assert self.default_value is not None

            mini_language_type = MiniLanguageHelpers.EvalTypeExpression(self.type, [])
            if not isinstance(mini_language_type, MiniLanguageHelpers.MiniLanguageType):
                errors.append(
                    InvalidTemplateDecoratorTypeError.Create(
                        region=self.type.regions__.self__,
                    ),
                )
            else:
                mini_language_expression = MiniLanguageHelpers.EvalExpression(self.default_value, [])

                if not mini_language_type.IsSupportedValue(mini_language_expression.value):
                    errors.append(
                        InvalidTypeError.Create(
                            region=self.default_value.regions__.self__,
                            expected_type=mini_language_type.name,
                            expected_region=self.type.regions__.self__,
                            actual_type=mini_language_expression.type.name,
                        ),
                    )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        yield "type", self.type  # type: ignore

        if self.default_value is not None:
            yield "default_value", self.default_value  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateParametersParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    # |  Public Types
    ParameterType                           = Union[
        TemplateTypeParameterParserInfo,
        TemplateDecoratorParameterParserInfo,
    ]

    # ----------------------------------------------------------------------
    # |  Public Data
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    positional: Optional[List["TemplateParametersParserInfo.ParameterType"]]
    any: Optional[List["TemplateParametersParserInfo.ParameterType"]]
    keyword: Optional[List["TemplateParametersParserInfo.ParameterType"]]

    is_default_initializable: bool          = field(init=False, default=False)

    call_helpers_positional: List[CallHelpers.ParameterInfo]                = field(init=False, default_factory=list)
    call_helpers_any: List[CallHelpers.ParameterInfo]                       = field(init=False, default_factory=list)
    call_helpers_keyword: List[CallHelpers.ParameterInfo]                   = field(init=False, default_factory=list)

    # ----------------------------------------------------------------------
    # |  Public Methods
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(TemplateParametersParserInfo, self).__init__(
            ParserInfoType.GetDominantType(
                *itertools.chain(
                    self.positional or [],
                    self.any or [],
                    self.keyword or [],
                ),
            ),
            *args,
            **{
                **kwargs,
                **{
                    "regionless_attributes": [
                        "is_default_initializable",
                        "call_helpers_positional",
                        "call_helpers_any",
                        "call_helpers_keyword",
                    ],
                    "is_default_initializable": None,
                    "call_helpers_positional": None,
                    "call_helpers_any": None,
                    "call_helpers_keyword": None,
                },
            },
        )

        assert self.positional or self.any or self.keyword

        is_default_initializable = True

        for template in itertools.chain(
            (self.positional or []),
            (self.any or []),
            (self.keyword or [])
        ):
            if isinstance(template, TemplateTypeParameterParserInfo):
                if template.default_type is None:
                    is_default_initializable = False
                    break
            elif isinstance(template, TemplateDecoratorParameterParserInfo):
                if template.default_value is None:
                    is_default_initializable = False
                    break

        object.__setattr__(self, "is_default_initializable", is_default_initializable)

        # Validate
        errors: List[Error] = []

        name_lookup: Dict[str, TemplateParametersParserInfo.ParameterType] = {}
        prev_variadic_parameter: Optional[TemplateParametersParserInfo.ParameterType] = None

        for parameter in itertools.chain(
            self.positional or [],
            self.any or [],
            self.keyword or [],
        ):
            # Check for duplicated names
            prev_parameter = name_lookup.get(parameter.name, None)
            if prev_parameter is not None:
                errors.append(
                    DuplicateNameError.Create(
                        region=parameter.regions__.name,
                        name=parameter.name,
                        prev_region=prev_parameter.regions__.name,
                    ),
                )
            else:
                name_lookup[parameter.name] = parameter

            # Check for multiple variadic parameters
            if getattr(parameter, "is_variadic", False):
                if prev_variadic_parameter is not None:
                    errors.append(
                        DuplicateVariadicError.Create(
                            region=parameter.regions__.is_variadic,
                            prev_region=prev_variadic_parameter.regions__.is_variadic,
                        ),
                    )
                else:
                    prev_variadic_parameter = parameter

        if errors:
            raise ErrorException(*errors)

        # Initialize the call helpers info
        for source_parameters, destination_attribute_name in [
            (self.positional, "call_helpers_positional"),
            (self.any, "call_helpers_any"),
            (self.keyword, "call_helpers_keyword"),
        ]:
            call_helpers_parameters: List[CallHelpers.ParameterInfo] = []

            for source_parameter in (source_parameters or []):
                if isinstance(source_parameter, TemplateTypeParameterParserInfo):
                    has_default = bool(source_parameter.default_type)
                    is_variadic = source_parameter.is_variadic is True

                elif isinstance(source_parameter, TemplateDecoratorParameterParserInfo):
                    has_default = bool(source_parameter.default_value)
                    is_variadic = False

                else:
                    assert False, source_parameter  # pragma: no cover

                call_helpers_parameters.append(
                    CallHelpers.ParameterInfo(
                        name=source_parameter.name,
                        region=source_parameter.regions__.self__,
                        is_optional=has_default,
                        is_variadic=is_variadic,
                        context=source_parameter,
                    ),
                )

            object.__setattr__(self, destination_attribute_name, call_helpers_parameters)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        if self.positional is not None:
            yield "positional", self.positional  # type: ignore

        if self.any is not None:
            yield "any", self.any  # type: ignore

        if self.keyword is not None:
            yield "keyword", self.keyword  # type: ignore
