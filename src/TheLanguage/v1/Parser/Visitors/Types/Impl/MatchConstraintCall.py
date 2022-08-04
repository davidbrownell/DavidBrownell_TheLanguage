# ----------------------------------------------------------------------
# |
# |  MatchConstraintCall.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-21 09:00:14
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality used when attempting to match constraint arguments to constraint parameters"""

import os

from typing import Any, List, Optional, Tuple

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ....Common import CallHelpers
    from ....Common import MiniLanguageHelpers

    from ....Error import Error, ErrorException

    from ....ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentParserInfo, ConstraintArgumentsParserInfo

    from ....ParserInfos.Common.ConstraintParametersParserInfo import (
        ConstraintParameterParserInfo,
        ConstraintParametersParserInfo,
        InvalidTypeError as InvalidConstraintTypeError,
    )

    from ....ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ....ParserInfos.Types.TypeResolver import TypeResolver

    from ....TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ResolvedArguments(object):
    decorators: List[
        Tuple[
            ConstraintParameterParserInfo,
            MiniLanguageHelpers.MiniLanguageExpression.EvalResult,
        ],
    ]

    cache_key: Tuple[Any, ...]              = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        cache_key = tuple(decorator[1].value for decorator in self.decorators)

        object.__setattr__(self, "cache_key", cache_key)


# ----------------------------------------------------------------------
def Match(
    constraint_parameters: ConstraintParametersParserInfo,
    constraint_arguments: Optional[ConstraintArgumentsParserInfo],
    destination: str,
    destination_region: TranslationUnitRegion,
    invocation_region: TranslationUnitRegion,
    type_resolver: TypeResolver,
) -> ResolvedArguments:
    if constraint_arguments is None:
        args = []
        kwargs = {}
    else:
        args = constraint_arguments.call_helpers_args
        kwargs = constraint_arguments.call_helpers_kwargs

    argument_map = CallHelpers.CreateArgumentMap(
        destination,
        destination_region,
        invocation_region,
        constraint_parameters.call_helpers_positional,
        constraint_parameters.call_helpers_any,
        constraint_parameters.call_helpers_keyword,
        args,
        kwargs,
    )

    # If here, we know that the arguments match up in terms of number, defaults, names, etc.
    # Validate that they match types as well.
    decorators: List[Tuple[ConstraintParameterParserInfo, MiniLanguageHelpers.MiniLanguageExpression.EvalResult]] = []
    errors: List[Error] = []

    for parameter_parser_info, argument_value in argument_map.values():
        if argument_value is None:
            assert parameter_parser_info.default_value is not None
            argument_value = parameter_parser_info.default_value
        else:
            # Decorators cannot be variadic
            assert isinstance(argument_value, ConstraintArgumentParserInfo), argument_value
            argument_value = argument_value.expression

        assert isinstance(argument_value, ExpressionParserInfo), argument_value

        resolved_type = type_resolver.EvalMiniLanguageType(parameter_parser_info.type)
        resolved_value = type_resolver.EvalMiniLanguageExpression(argument_value)

        if not resolved_type.IsSupportedValue(resolved_value.value):
            errors.append(
                InvalidConstraintTypeError.Create(
                    region=argument_value.regions__.self__,
                    expected_type=resolved_type.name,
                    expected_region=parameter_parser_info.type.regions__.self__,
                    actual_type=resolved_value.type.name,
                ),
            )

            continue

        decorators.append((parameter_parser_info, resolved_value))

    if errors:
        raise ErrorException(*errors)

    return ResolvedArguments(decorators)
