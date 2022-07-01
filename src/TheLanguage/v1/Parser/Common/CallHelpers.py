# ----------------------------------------------------------------------
# |
# |  CallHelpers.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-05-02 11:23:40
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that helps when calling functions"""

import itertools
import os

from typing import Any, cast, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Error import CreateError, Error, ErrorException, TranslationUnitRegion


# ----------------------------------------------------------------------
InvalidKeywordError                         = CreateError(
    "Arguments for the positional parameter '{name}' can not be explicitly named in the call to '{destination}'",
    destination=str,
    destination_region=Optional[TranslationUnitRegion],
    name=str,
    parameter_region=Optional[TranslationUnitRegion],
)

InvalidKeywordArgumentError                 = CreateError(
    "'{name}' is not a valid parameter in '{destination}'",
    destination=str,
    destination_region=Optional[TranslationUnitRegion],
    name=str,
)

DuplicateKeywordArgumentError               = CreateError(
    "The argument '{name}' has already been provided in the call to '{destination}'",
    destination=str,
    destination_region=Optional[TranslationUnitRegion],
    name=str,
    prev_region=TranslationUnitRegion,
)

TooManyArgumentsError                       = CreateError(
    "Too many arguments in the call to '{destination}'",
    destination=str,
    destination_region=Optional[TranslationUnitRegion],
)

RequiredArgumentMissingError                = CreateError(
    "An argument for the parameter '{name}' is missing in the call to '{destination}'",
    destination=str,
    destination_region=Optional[TranslationUnitRegion],
    name=str,
)


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParameterInfo(object):
    name: str
    region: Optional[TranslationUnitRegion]
    is_optional: bool
    is_variadic: bool
    context: Any


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ArgumentInfo(object):
    region: Optional[TranslationUnitRegion]
    context: Any


# ----------------------------------------------------------------------
def CreateArgumentMap(
    destination: str,
    destination_region: Optional[TranslationUnitRegion],
    positional_parameters: List[ParameterInfo],
    any_parameters: List[ParameterInfo],
    keyword_parameters: List[ParameterInfo],
    args: List[ArgumentInfo],
    kwargs: Dict[str, ArgumentInfo],
) -> Dict[
    str,
    Tuple[
        Any,                                # Parameter's context
        Union[
            Any,                            # Argument's context
            List[Any],                      # Argument's context for arguments associated with variadic parameters
        ],
    ],
]:
    """\
    Returns a dictionary that can be used to dynamically invoke the destination function with
    the specified parameters.
    """

    all_results: Dict[
        str,
        Tuple[
            ParameterInfo,
            Union[
                ArgumentInfo,
                List[ArgumentInfo],
            ],
        ],
    ] = {}

    errors: List[Error] = []

    # Process the arguments specified by keyword
    if kwargs:
        valid_keywords: Dict[str, ParameterInfo] = {
            parameter.name : parameter
            for parameter in itertools.chain(any_parameters, keyword_parameters)
        }

        for key, value in kwargs.items():
            potential_parameter = valid_keywords.get(key, None)

            if potential_parameter is None:
                # This is a problem. Determine which type of error to provide.
                potential_positional_parameter = next(
                    (parameter for parameter in positional_parameters if parameter.name == key),
                    None,
                )

                if potential_positional_parameter is not None:
                    errors.append(
                        InvalidKeywordError.Create(
                            region=value.region,
                            destination=destination,
                            destination_region=destination_region,
                            name=key,
                            parameter_region=potential_positional_parameter.region,
                        ),
                    )
                else:
                    errors.append(
                        InvalidKeywordArgumentError.Create(
                            region=value.region,
                            destination=destination,
                            destination_region=destination_region,
                            name=key,
                        ),
                    )

                continue

            existing_result_or_results = all_results.get(potential_parameter.name, _does_not_exist)

            if isinstance(existing_result_or_results, _DoesNotExist):
                if potential_parameter.is_variadic:
                    value = [value, ]

                all_results[key] = (potential_parameter, value)

            elif potential_parameter.is_variadic:
                assert isinstance(existing_result_or_results, tuple), existing_result_or_results
                assert isinstance(existing_result_or_results[1], list), existing_result_or_results[1]
                existing_result_or_results[1].append(value)

            else:
                assert isinstance(existing_result_or_results, tuple), existing_result_or_results
                assert isinstance(existing_result_or_results[1], ArgumentInfo), existing_result_or_results[1]

                errors.append(
                    DuplicateKeywordArgumentError.Create(
                        region=value.region,
                        destination=destination,
                        destination_region=destination_region,
                        name=potential_parameter.name,
                        prev_region=existing_result_or_results[1].region,
                    ),
                )

    # Process the arguments specified by position
    if args:
        all_positional_parameters: List[ParameterInfo] = positional_parameters + any_parameters
        all_positional_parameters_index = 0

        for arg in args:
            potential_parameter: Optional[ParameterInfo] = None

            while all_positional_parameters_index < len(all_positional_parameters):
                potential_parameter = all_positional_parameters[all_positional_parameters_index]

                if potential_parameter.is_variadic:
                    break

                if potential_parameter.name not in all_results:
                    break

                all_positional_parameters_index += 1

            if all_positional_parameters_index == len(all_positional_parameters):
                errors.append(
                    TooManyArgumentsError.Create(
                        region=arg.region,
                        destination=destination,
                        destination_region=destination_region,
                    ),
                )
                break

            assert potential_parameter is not None

            if potential_parameter.is_variadic:
                existing_result = all_results.get(potential_parameter.name, None)
                if existing_result is not None:
                    assert isinstance(existing_result, tuple), existing_result
                    assert isinstance(existing_result[1], list), existing_result[1]

                    existing_result[1].append(arg)
                else:
                    all_results[potential_parameter.name] = (potential_parameter, [arg, ])

            else:
                assert potential_parameter.name not in all_results, potential_parameter.name
                all_results[potential_parameter.name] = (potential_parameter, arg)

    raw_results = {}

    for k, results in all_results.items():
        assert isinstance(results, tuple), results

        if isinstance(results[1], list):
            raw_result = (results[0].context, [arg.context for arg in results[1]])
        else:
            raw_result = results[0].context, results[1].context

        raw_results[k] = raw_result

    # Have all arguments been provided?
    for parameter in itertools.chain(positional_parameters, any_parameters, keyword_parameters):
        if parameter.name not in all_results:
            if not parameter.is_optional:
                errors.append(
                    RequiredArgumentMissingError.Create(
                        region=parameter.region,
                        destination=destination,
                        destination_region=destination_region,
                        name=parameter.name,
                    ),
                )
            elif parameter.is_variadic:
                raw_results[parameter.name] = [(parameter.context, None)]
            else:
                raw_results[parameter.name] = (parameter.context, None)

    if errors:
        raise ErrorException(*errors)

    return raw_results


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _DoesNotExist(object):
    pass


# ----------------------------------------------------------------------
# |
# |  Private Data
# |
# ----------------------------------------------------------------------
_does_not_exist                             = _DoesNotExist()
