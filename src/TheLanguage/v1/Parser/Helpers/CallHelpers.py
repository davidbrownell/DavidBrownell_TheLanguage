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

from typing import Any, cast, Dict, List, Optional, Union

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


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ArgumentInfo(object):
    value: Any
    region: Optional[TranslationUnitRegion]


# ----------------------------------------------------------------------
def CreateArgumentMap(
    destination: str,
    destination_region: Optional[TranslationUnitRegion],
    positional_parameters: List[ParameterInfo],
    any_parameters: List[ParameterInfo],
    keyword_parameters: List[ParameterInfo],
    args: List[ArgumentInfo],
    kwargs: Dict[str, ArgumentInfo],
) -> Dict[str, Any]:
    """\
    Returns a dictionary that can be used to dynamically invoke the destination function with
    the specified parameters.
    """

    result: Dict[str, Union[ArgumentInfo, List[ArgumentInfo]]] = {}
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

            potential_argument_value = result.get(potential_parameter.name, _does_not_exist)

            if isinstance(potential_argument_value, _DoesNotExist):
                if potential_parameter.is_variadic:
                    value = [value, ]

                result[key] = value

            elif potential_parameter.is_variadic:
                assert isinstance(potential_argument_value, list), potential_argument_value
                potential_argument_value.append(value)

            else:
                assert isinstance(potential_argument_value, ArgumentInfo), potential_argument_value

                errors.append(
                    DuplicateKeywordArgumentError.Create(
                        region=value.region,
                        destination=destination,
                        destination_region=destination_region,
                        name=potential_parameter.name,
                        prev_region=potential_argument_value.region,
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

                if potential_parameter.name not in result:
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
                cast(List[ArgumentInfo], result.setdefault(potential_parameter.name, [])).append(arg)
            else:
                assert potential_parameter.name not in result, potential_parameter.name
                result[potential_parameter.name] = arg

    result = result
    raw_arguments = {}

    for k, v in result.items():
        if isinstance(v, list):
            v = [item.value for item in v]
        else:
            v = v.value

        raw_arguments[k] = v

    # Have all arguments been provided?
    for parameter in itertools.chain(positional_parameters, any_parameters, keyword_parameters):
        if parameter.name not in result:
            if not parameter.is_optional:
                errors.append(
                    RequiredArgumentMissingError.Create(
                        region=parameter.region,
                        destination=destination,
                        destination_region=destination_region,
                        name=parameter.name,
                    ),
                )
            else:
                raw_arguments[parameter.name] = None

    if errors:
        raise ErrorException(*errors)

    return raw_arguments


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
