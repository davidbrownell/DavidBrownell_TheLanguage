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

from typing import Any, Callable, cast, Dict, List, Optional, Union, TYPE_CHECKING

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.TemplateParametersParserInfo import TemplateTypeParameterParserInfo

    from ..Expressions.ExpressionParserInfo import (
        ExpressionParserInfo,
        ParserInfo,
        ParserInfoType,
        TranslationUnitRegion,
    )

    from ..Expressions.Traits.SimpleExpressionTrait import SimpleExpressionTrait

    from ..Statements.StatementParserInfo import StatementParserInfo

    from ...Common import CallHelpers
    from ...Common import MiniLanguageHelpers

    from ...Error import CreateError, Error, ErrorException

    if TYPE_CHECKING:
        from .TemplateArgumentsParserInfo import TemplateArgumentsParserInfo


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
            regionless_attributes=[
                "type",
                "default_value",
                "is_simple_expression__",
            ],
            **{
                **{
                    "is_simple_expression__": None,
                },
                **kwargs,
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

    default_initializable: bool             = field(init=False, default=False)

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
            regionless_attributes=[
                "default_initializable",
                "call_helpers_positional",
                "call_helpers_any",
                "call_helpers_keyword",
            ],
            **{
                **{
                    "default_initializable": None,
                    "call_helpers_positional": None,
                    "call_helpers_any": None,
                    "call_helpers_keyword": None,
                },
                **kwargs,
            },
        )

        assert self.positional or self.any or self.keyword

        default_initializable = True

        for constraint in itertools.chain(
            (self.positional or []),
            (self.any or []),
            (self.keyword or []),
        ):
            if constraint.default_value is None:
                default_initializable = False
                break

        object.__setattr__(self, "default_initializable", default_initializable)

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

    # BugBug # ----------------------------------------------------------------------
    # BugBug def MatchCall(
    # BugBug     self,
    # BugBug     destination: str,
    # BugBug     destination_region: TranslationUnitRegion,
    # BugBug     invocation_region: TranslationUnitRegion,
    # BugBug     constraint_arguments: Optional["ConstraintArgumentsParserInfo"],
    # BugBug     resolve_type_func: Callable[[ExpressionParserInfo], MiniLanguageHelpers.MiniLanguageType],
    # BugBug     resolve_value_func: Callable[[ExpressionParserInfo], MiniLanguageHelpers.MiniLanguageExpression.EvalResult],
    # BugBug ) -> Dict[str, Any]:
    # BugBug     # BugBug: This needs work, as TemplateParametersParserInfo.MatchCall has undergone changes.
    # BugBug
    # BugBug     if constraint_arguments is None:
    # BugBug         args = []
    # BugBug         kwargs = {}
    # BugBug     else:
    # BugBug         args = constraint_arguments.call_helpers_args
    # BugBug         kwargs = constraint_arguments.call_helpers_kwargs
    # BugBug
    # BugBug     argument_map = CallHelpers.CreateArgumentMap(
    # BugBug         destination,
    # BugBug         destination_region,
    # BugBug         invocation_region,
    # BugBug         self.call_helpers_positional,
    # BugBug         self.call_helpers_any,
    # BugBug         self.call_helpers_keyword,
    # BugBug         args,
    # BugBug         kwargs,
    # BugBug     )
    # BugBug
    # BugBug     # If here, we know that the arguments match up in terms of number, defaults, names, etc.
    # BugBug     errors: List[Error] = []
    # BugBug
    # BugBug     for name, (parameter_parser_info, argument_parser_info) in argument_map.items():
    # BugBug         if argument_parser_info is None:
    # BugBug             argument_parser_info = parameter_parser_info.default_value
    # BugBug             assert isinstance(argument_parser_info, ExpressionParserInfo)
    # BugBug         else:
    # BugBug             assert argument_parser_info.__class__.__name__ == "ConstraintArgumentParserInfo", argument_parser_info.__class__
    # BugBug             argument_parser_info = cast("ArgumentParserInfo", argument_parser_info)  # type: ignore
    # BugBug
    # BugBug             assert not argument_parser_info.expression.IsType()
    # BugBug             argument_parser_info = argument_parser_info.expression
    # BugBug
    # BugBug         resolved_type = resolve_type_func(parameter_parser_info.type)
    # BugBug         resolved_value = resolve_value_func(argument_parser_info)
    # BugBug
    # BugBug         if not resolved_type.IsSupportedValue(resolved_value.value):
    # BugBug             errors.append(
    # BugBug                 InvalidTypeError.Create(
    # BugBug                     region=argument_parser_info.regions__.self__,
    # BugBug                     expected_type=resolved_type.name,
    # BugBug                     expected_region=parameter_parser_info.type.regions__.self__,
    # BugBug                     actual_type=resolved_value.type.name,
    # BugBug                 ),
    # BugBug             )
    # BugBug
    # BugBug             continue
    # BugBug
    # BugBug         argument_map[name] = (parameter_parser_info, resolved_value)
    # BugBug
    # BugBug     if errors:
    # BugBug         raise ErrorException(*errors)
    # BugBug
    # BugBug     return argument_map

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
