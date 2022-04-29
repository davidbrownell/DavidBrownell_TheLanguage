# ----------------------------------------------------------------------
# |
# |  BaseMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-27 13:44:27
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the BaseMixin object"""

import itertools
import os
import types

from typing import Any, cast, Dict, List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StateMaintainer import StateMaintainer

    from ...Error import CreateError, Error, ErrorException, Warning, Info

    from ...MiniLanguage.Types.Type import Type as MiniLanguageType

    from ...ParserInfos.ParserInfo import ParserInfo, Region, VisitControl
    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier


# ----------------------------------------------------------------------
InvalidKeywordError                         = CreateError(
    "The argument '{name}' was explicitly named, but it is defined as a positional parameter in '{destination}'",
    destination=str,
    destination_region=Optional[Region],
    name=str,
    parameter_region=Optional[Region],
)

InvalidKeywordArgumentError                 = CreateError(
    "'{name}' is not a valid parameter name in '{destination}'",
    destination=str,
    destination_region=Optional[Region],
    name=str,
)

TooManyArgumentsError                       = CreateError(
    "Too many arguments were provided to '{destination}'",
    destination=str,
    destination_region=Optional[Region],
)

DuplicateKeywordArgumentError               = CreateError(
    "The argument '{name}' has already been provided to '{destination}'",
    destination=str,
    destination_region=Optional[Region],
    name=str,
    prev_region=Region,
)

RequiredArgumentMissingError                = CreateError(
    "An argument for the parameter '{name}' is missing for '{destination}'",
    destination=str,
    destination_region=Optional[Region],
    name=str,
)


# ----------------------------------------------------------------------
class CompileTimeTemplateTypeWrapper(object):
    pass


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class CompileTimeVariable(object):
    type: Union[CompileTimeTemplateTypeWrapper, MiniLanguageType]
    value: Any
    parser_info: ParserInfo


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ParameterInfo(object):
    name: str
    region: Optional[Region]
    is_optional: bool
    is_variadic: bool


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ArgumentInfo(object):
    value: Any
    region: Region


# ----------------------------------------------------------------------
class BaseMixin(object):
    """Base class for all mixins associated with this visitor"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        compile_time_info: Dict[str, CompileTimeVariable],
    ):
        self._compile_time_info             = StateMaintainer[CompileTimeVariable](compile_time_info)  # type: ignore

        self._errors: List[Error]           = []
        self._warnings: List[Warning]       = []
        self._infos: List[Info]             = []

        self._scope_level                                                   = 0
        self._scope_delta                                                   = 0
        self._exports: Dict[VisibilityModifier, List[ParserInfo]]           = {}

    # ----------------------------------------------------------------------
    @property
    def errors(self) -> List[Error]:
        return self._errors

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        if name.startswith("OnExit"):
            return self.__class__._DefaultOnExitMethod  # pylint: disable=protected-access
        elif name.startswith("OnEnter"):
            name = "On{}".format(name[len("OnEnter"):])

            method = getattr(self, name, None)
            assert method is not None, name

            return method

        index = name.find("ParserInfo__")
        if index != -1 and index + len("ParserInfo__") + 1 < len(name):
            return types.MethodType(self.__class__._DefaultDetailMethod, self)

        return None

    # ----------------------------------------------------------------------
    @staticmethod
    def OnEnterPhrase(
        parser_info: ParserInfo,  # pylint: disable=unused-argument
    ):
        pass

    # ----------------------------------------------------------------------
    def OnExitPhrase(
        self,
        parser_info: ParserInfo,
    ):
        if self._scope_level + self._scope_delta == 1:
            pass # TODO

    # ----------------------------------------------------------------------
    def OnEnterScope(
        self,
        parser_info: ParserInfo,  # pylint: disable=unused-argument
    ) -> None:
        self._PushScope()

    # ----------------------------------------------------------------------
    def OnExitScope(
        self,
        parser_info: ParserInfo,  # pylint: disable=unused-argument
    ) -> None:
        self._PopScope()

    # ----------------------------------------------------------------------
    @staticmethod
    def OnRootParserInfo(
        parser_info: ParserInfo,  # pylint: disable=unused-argument
    ):
        pass

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _PushScope(self):
        self._scope_level += 1
        self._compile_time_info.PushScope()

    # ----------------------------------------------------------------------
    def _PopScope(self):
        self._compile_time_info.PopScope()

        assert self._scope_level
        self._scope_level -= 1

    # ----------------------------------------------------------------------
    @classmethod
    def _CreateArgumentMap(
        cls,
        destination: str,
        destination_region: Optional[Region],
        positional_parameters: List[ParameterInfo],
        any_parameters: List[ParameterInfo],
        keyword_parameters: List[ParameterInfo],
        args: List[ArgumentInfo],
        kwargs: Dict[str, ArgumentInfo],
    ) -> Dict[
        str,
        Union[
            ArgumentInfo,                   # Standard arguments
            List[ArgumentInfo],             # Variadic arguments
        ]
    ]:
        """Creates a map of arguments that can be passed to an entity requiring the specified positional and keyword parameters"""

        results: Dict[str, Union[ArgumentInfo, List[ArgumentInfo]]] = {}
        errors: List[Error] = []

        # Process the arguments specified by keyword
        if kwargs:
            valid_keywords: Dict[str, ParameterInfo] = {
                parameter.name : parameter
                for parameter in itertools.chain(any_parameters + keyword_parameters)
            }

            for key, value in kwargs.items():
                potential_parameter = valid_keywords.get(key, None)

                if potential_parameter is None:
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

                potential_argument_value = results.get(potential_parameter.name, cls._does_not_exist)

                if isinstance(potential_argument_value, cls._DoesNotExist):
                    if potential_parameter.is_variadic:
                        value = [value, ]

                    results[key] = value

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

                    if potential_parameter.name not in results:
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
                    cast(List[ArgumentInfo], results.setdefault(potential_parameter.name, [])).append(arg)
                else:
                    assert potential_parameter.name not in results, potential_parameter.name
                    results[potential_parameter.name] = arg

        # Have all values been provided?
        for parameter in itertools.chain(positional_parameters, any_parameters, keyword_parameters):
            if parameter.name not in results and not parameter.is_optional:
                errors.append(
                    RequiredArgumentMissingError.Create(
                        region=parameter.region,
                        destination=destination,
                        destination_region=destination_region,
                        name=parameter.name,
                    ),
                )

        if errors:
            raise ErrorException(*errors)

        return results

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    class _DoesNotExist(object):
        pass

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _does_not_exist                         = _DoesNotExist()

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    def _DefaultDetailMethod(
        self,
        parser_info_or_infos: Union[ParserInfo, List[ParserInfo]],
    ):
        if isinstance(parser_info_or_infos, list):
            for parser_info in parser_info_or_infos:
                visit_control = parser_info.Accept(self)

                if visit_control == VisitControl.Terminate:
                    return visit_control

                if visit_control == VisitControl.SkipSiblings:
                    break

            return VisitControl.Continue

        return parser_info_or_infos.Accept(self)

    # ----------------------------------------------------------------------
    @staticmethod
    def _DefaultOnExitMethod(
        parser_info: ParserInfo,  # pylint: disable=unused-argument
    ):
        pass
