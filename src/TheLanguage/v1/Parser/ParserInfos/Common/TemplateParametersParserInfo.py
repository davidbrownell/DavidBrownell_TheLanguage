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

from typing import Dict, List, Optional, Union

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Expressions.ExpressionParserInfo import (
        ExpressionParserInfo,
        ParserInfo,
        ParserInfoType,
        TranslationUnitRegion,
    )

    from ..Statements.StatementParserInfo import StatementParserInfo

    from ...Error import CreateError, Error, ErrorException


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

InvalidTemplateTypeError                    = CreateError(
    "Template type parameters must be compile-time types",
)

InvalidTemplateDecoratorTypeError           = CreateError(
    "Template decorator parameters must be compile-time types",
)

InvalidTemplateDecoratorExpressionError     = CreateError(
    "Template decorator parameters must be compile-time expressions",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateTypeParameterParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    name: str
    is_variadic: Optional[bool]
    default_type: Optional[ExpressionParserInfo]

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
        super(TemplateTypeParameterParserInfo, self).__init__(
            ParserInfoType.TypeCustomization,
            *args,
            **kwargs,
            regionless_attributes=["default_type", ],
        )

        # Validate
        errors: List[Error] = []

        if self.default_type:
            try:
                self.default_type.InitializeAsType(self.parser_info_type__)

                if self.default_type.parser_info_type__ != self.parser_info_type__:
                    errors.append(
                        InvalidTemplateTypeError.Create(
                            region=self.default_type.regions__.self__,
                        ),
                    )
            except ErrorException as ex:
                errors += ex.errors

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        if self.default_type is not None:
            yield "default_type", self.default_type  # type: ignore


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class TemplateDecoratorParameterParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    type: ExpressionParserInfo
    name: str
    default_value: Optional[ExpressionParserInfo]

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
            **kwargs,
            regionless_attributes=[
                "type",
                "default_value",
            ],
        )

        # Validate
        errors: List[Error] = []

        try:
            self.type.InitializeAsType(ParserInfoType.TypeCustomization)

            if self.type.parser_info_type__ != ParserInfoType.TypeCustomization:
                errors.append(
                    InvalidTemplateDecoratorTypeError.Create(
                        region=self.type.regions__.self__,
                    ),
                )
        except ErrorException as ex:
            errors += ex.errors

        if self.default_value is not None:
            try:
                self.default_value.InitializeAsExpression()

                if not ParserInfoType.IsCompileTime(self.default_value.parser_info_type__):
                    errors.append(
                        InvalidTemplateDecoratorExpressionError.Create(
                            region=self.default_value.regions__.self__,
                        ),
                    )
            except ErrorException as ex:
                errors += ex.errors

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
            **kwargs,
        )

        assert self.positional or self.any or self.keyword

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
