# ----------------------------------------------------------------------
# |
# |  ConstraintParametersParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-14 09:58:23
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about constraint parameters"""

import itertools
import os

from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

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

    from ..Expressions.Traits.SimpleExpressionTrait import SimpleExpressionTrait

    from ...Common import CallHelpers
    from ...Common import MiniLanguageHelpers

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The constraint parameter '{name}' has already been defined",
    name=str,
    prev_region=TranslationUnitRegion,
)

InvalidConstraintTypeError                  = CreateError(
    "Constraint parameter types must be compile-time types",
)

InvalidConstraintExpressionError            = CreateError(
    "Constraint parameter values must be compile-time expressions",
)

InvalidTypeError                            = CreateError(
    "Invalid constraint value; '{expected_type}' expected but '{actual_type}' was found",
    expected_type=str,
    expected_region=TranslationUnitRegion,
    actual_type=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class ConstraintParameterParserInfo(ParserInfo):
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
        super(ConstraintParameterParserInfo, self).__init__(
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
            self.type.InitializeAsType(self.parser_info_type__)

            if not self.type.is_compile_time__:
                errors.append(
                    InvalidConstraintTypeError.Create(
                        region=self.type.regions__.self__,
                    ),
                )
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
                        InvalidConstraintExpressionError.Create(
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
                    InvalidConstraintTypeError.Create(
                        region=self.type.regions__.self__,
                    ),
                )
            else:
                resolved_expression = MiniLanguageHelpers.EvalExpression(self.default_value, [])

                if not mini_language_type.IsSupportedValue(resolved_expression.value):
                    errors.append(
                        InvalidTypeError.Create(
                            region=self.default_value.regions__.self__,
                            expected_type=mini_language_type.name,
                            expected_region=self.type.regions__.self__,
                            actual_type=resolved_expression.type.name,
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
class ConstraintParametersParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    regions: InitVar[List[Optional[TranslationUnitRegion]]]

    positional: Optional[List[ConstraintParameterParserInfo]]
    any: Optional[List[ConstraintParameterParserInfo]]
    keyword: Optional[List[ConstraintParameterParserInfo]]

    is_default_initializable: bool          = field(init=False, default=False)

    call_helpers_positional: List[CallHelpers.ParameterInfo]                = field(init=False, default_factory=list)
    call_helpers_any: List[CallHelpers.ParameterInfo]                       = field(init=False, default_factory=list)
    call_helpers_keyword: List[CallHelpers.ParameterInfo]                   = field(init=False, default_factory=list)

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
        super(ConstraintParametersParserInfo, self).__init__(
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
        )

        assert self.positional or self.any or self.keyword

        is_default_initializable = True

        for constraint in itertools.chain(
            (self.positional or []),
            (self.any or []),
            (self.keyword or []),
        ):
            if constraint.default_value is None:
                is_default_initializable = False
                break

        object.__setattr__(self, "is_default_initializable", is_default_initializable)

        # Validate
        errors: List[Error] = []

        name_lookup: Dict[str, ConstraintParameterParserInfo] = {}

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
                call_helpers_parameters.append(
                    CallHelpers.ParameterInfo(
                        name=source_parameter.name,
                        region=source_parameter.regions__.self__,
                        is_optional=source_parameter.default_value is not None,
                        is_variadic=False,
                        context=source_parameter,
                    ),
                )

            object.__setattr__(self, destination_attribute_name, call_helpers_parameters)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.override
    def _GenerateAcceptDetails(self) -> ParserInfo._GenerateAcceptDetailsResultType:  # pylint: disable=protected-access
        if self.positional:
            yield "positional", self.positional  # type: ignore

        if self.any:
            yield "any", self.any  # type: ignore

        if self.keyword:
            yield "keyword", self.keyword  # type: ignore
