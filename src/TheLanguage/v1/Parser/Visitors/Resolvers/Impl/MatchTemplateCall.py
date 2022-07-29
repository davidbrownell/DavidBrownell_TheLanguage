# ----------------------------------------------------------------------
# |
# |  MatchTemplateCall.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-20 09:49:02
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality used when attempting to match template arguments to template parameters"""

import os

from typing import Any, List, Optional, Tuple, Union

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

    from ....ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo, TemplateArgumentParserInfo

    from ....ParserInfos.Common.TemplateParametersParserInfo import (
        InvalidTypeError as InvalidTemplateTypeError,
        TemplateParametersParserInfo,
        TemplateDecoratorParameterParserInfo,
        TemplateTypeParameterParserInfo,
    )

    from ....ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo

    from ....ParserInfos.Types.ConcreteType import ConcreteType
    from ....ParserInfos.Types.TypeResolvers import TypeResolver

    from ....TranslationUnitRegion import TranslationUnitRegion


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ResolvedArguments(object):
    types: List[
        Tuple[
            TemplateTypeParameterParserInfo,
            Union[ConcreteType, List[ConcreteType]],
        ],
    ]

    decorators: List[
        Tuple[
            TemplateDecoratorParameterParserInfo,
            MiniLanguageHelpers.MiniLanguageExpression.EvalResult,
        ],
    ]

    cache_key: Tuple[Any, ...]              = field(init=False)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        # BugBug: Types with cache_key
        types_cache_key = None

        decorators_cache_key = tuple(decorator[1].value for decorator in self.decorators)

        cache_key = (types_cache_key, decorators_cache_key)

        object.__setattr__(self, "cache_key", cache_key)


# ----------------------------------------------------------------------
def Match(
    template_parameters: TemplateParametersParserInfo,
    template_arguments: Optional[TemplateArgumentsParserInfo],
    destination: str,
    destination_region: TranslationUnitRegion,
    invocation_region: TranslationUnitRegion,
    type_resolver: TypeResolver,
) -> ResolvedArguments:
    if template_arguments is None:
        args = []
        kwargs = {}
    else:
        args = template_arguments.call_helpers_args
        kwargs = template_arguments.call_helpers_kwargs

    argument_map = CallHelpers.CreateArgumentMap(
        destination,
        destination_region,
        invocation_region,
        template_parameters.call_helpers_positional,
        template_parameters.call_helpers_any,
        template_parameters.call_helpers_keyword,
        args,
        kwargs,
    )

    # If here, we know that the arguments match up in terms of number, defaults, names, etc.
    # Validate that they match types as well.
    types: List[
        Tuple[
            TemplateTypeParameterParserInfo,
            Union[ConcreteType, List[ConcreteType]],
        ]
    ] = []
    decorators: List[Tuple[TemplateDecoratorParameterParserInfo, MiniLanguageHelpers.MiniLanguageExpression.EvalResult]] = []
    errors: List[Error] = []

    for parameter_parser_info, argument_value in argument_map.values():
        if isinstance(parameter_parser_info, TemplateTypeParameterParserInfo):
            if isinstance(argument_value, list):
                assert all(isinstance(argument, ExpressionParserInfo) for argument in argument_value), argument_value

                argument_result_or_results = [
                    type_resolver.EvalConcreteType(argument.type_or_expression)
                    for argument in argument_value
                ]
            else:
                if argument_value is None:
                    assert parameter_parser_info.default_type is not None
                    argument_value = parameter_parser_info.default_type
                else:
                    assert isinstance(argument_value, TemplateArgumentParserInfo), argument_value
                    argument_value = argument_value.type_or_expression

                assert isinstance(argument_value, ExpressionParserInfo), argument_value
                argument_result_or_results = type_resolver.EvalConcreteType(argument_value)

            types.append((parameter_parser_info, argument_result_or_results))

        elif isinstance(parameter_parser_info, TemplateDecoratorParameterParserInfo):
            if argument_value is None:
                assert parameter_parser_info.default_value is not None
                argument_value = parameter_parser_info.default_value
            else:
                # Decorators cannot be variadic
                assert isinstance(argument_value, TemplateArgumentParserInfo), argument_value
                argument_value = argument_value.type_or_expression

            assert isinstance(argument_value, ExpressionParserInfo), argument_value

            resolved_type = type_resolver.EvalMiniLanguageType(parameter_parser_info.type)
            resolved_value = type_resolver.EvalMiniLanguageExpression(argument_value)

            if not resolved_type.IsSupportedValue(resolved_value.value):
                errors.append(
                    InvalidTemplateTypeError.Create(
                        region=argument_value.regions__.self__,
                        expected_type=resolved_type.name,
                        expected_region=parameter_parser_info.type.regions__.self__,
                        actual_type=resolved_value.type.name,
                    ),
                )

                continue

            decorators.append((parameter_parser_info, resolved_value))

        else:
            assert False, parameter_parser_info  # pragma: no cover

    if errors:
        raise ErrorException(*errors)

    return ResolvedArguments(types, decorators)
