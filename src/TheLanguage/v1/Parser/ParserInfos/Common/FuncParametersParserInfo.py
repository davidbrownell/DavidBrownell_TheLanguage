# ----------------------------------------------------------------------
# |
# |  FuncParametersParserInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-11 16:43:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains information about function parameters"""

import itertools
import os

from typing import Dict, List, Optional

from dataclasses import dataclass, InitVar

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.MutabilityModifier import (
        InvalidNewMutabilityModifierError,
        MutabilityModifier,
        MutabilityModifierRequiredError,
    )

    from ..Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ..Types.TypeParserInfo import (
        ParserInfo,
        ParserInfoType,
        Region,
        TypeParserInfo,
    )

    from ...Error import CreateError, Error, ErrorException


# ----------------------------------------------------------------------
DuplicateNameError                          = CreateError(
    "The parameter name '{name}' has already been defined",
    name=str,
    prev_region=Region,
)

DuplicateVariadicError                      = CreateError(
    "A variadic parameter has already been defined",
    prev_region=Region,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncParameterParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[Region]]]

    is_compile_time: Optional[bool]

    type: TypeParserInfo
    is_variadic: Optional[bool]
    name: str
    default_value: Optional[ExpressionParserInfo]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: InitVar[List[Optional[Region]]],
        is_compile_time: bool,
        *args,
        **kwargs,
    ):
        if is_compile_time:
            parser_info_type = ParserInfoType.CompileTime
            is_compile_time_value = True
        else:
            parser_info_type = ParserInfoType.Standard
            is_compile_time_value = None

        return cls(
            parser_info_type,               # type: ignore
            regions,
            is_compile_time_value,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(FuncParameterParserInfo, self).__init__(
            *args,
            **kwargs,
            regionless_attributes=[
                "type",
                "default_value",
            ],
        )

        # Validate
        errors: List[Error] = []

        if self.type.mutability_modifier is None:
            errors.append(
                MutabilityModifierRequiredError.Create(
                    region=self.type.regions__.self__,
                ),
            )
        elif self.type.mutability_modifier == MutabilityModifier.new:
            errors.append(
                InvalidNewMutabilityModifierError.Create(
                    region=self.type.regions__.mutability_modifier,
                ),
            )

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.default_value is not None:
            details.append(("default_value", self.default_value))

        return self._AcceptImpl(
            visitor,
            details=[
                ("type", self.type),
            ] + details,  # type: ignore
            children=None,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class FuncParametersParserInfo(ParserInfo):
    # ----------------------------------------------------------------------
    parser_info_type: InitVar[ParserInfoType]
    regions: InitVar[List[Optional[Region]]]

    positional: Optional[List[FuncParameterParserInfo]]
    any: Optional[List[FuncParameterParserInfo]]
    keyword: Optional[List[FuncParameterParserInfo]]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        regions: List[Optional[Region]],
        positional: Optional[List[FuncParameterParserInfo]],
        any_args: Optional[List[FuncParameterParserInfo]],
        keyword: Optional[List[FuncParameterParserInfo]],
        *args,
        **kwargs,
    ):
        parser_info_type = cls._GetDominantExpressionType(
            *itertools.chain(
                positional or [],
                any_args or [],
                keyword or [],
            ),
        )

        if isinstance(parser_info_type, list):
            raise ErrorException(*parser_info_type)

        return cls(                         # pylint: disable=too-many-function-args
            parser_info_type,               # type: ignore
            regions,                        # type: ignore
            positional,
            any_args,
            keyword,
            *args,
            **kwargs,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self, *args, **kwargs):
        super(FuncParametersParserInfo, self).__init__(*args, **kwargs)
        assert self.positional or self.any or self.keyword

        # Validate
        errors: List[Error] = []

        name_lookup: Dict[str, FuncParameterParserInfo] = {}
        prev_variadic_parameter: Optional[FuncParameterParserInfo] = None

        # Check for duplicate names and multiple variadic parameters
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
            if parameter.is_variadic:
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
    @Interface.override
    def Accept(self, visitor):
        details = []

        if self.positional:
            details.append(("positional", self.positional))
        if self.any:
            details.append(("any", self.any))
        if self.keyword:
            details.append(("keyword", self.keyword))

        return self._AcceptImpl(
            visitor,
            details=details,
            children=None,
        )
