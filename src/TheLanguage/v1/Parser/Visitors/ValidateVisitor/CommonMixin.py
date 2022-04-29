# ----------------------------------------------------------------------
# |
# |  CommonMixin.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-27 13:45:48
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the CommonMixin object"""

import itertools
import os

from typing import Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import (
        BaseMixin,
        CompileTimeTemplateTypeWrapper,
        CompileTimeVariable,
        StateMaintainer,
        VisitControl,
    )

    from ...MiniLanguage.Types.BooleanType import BooleanType
    from ...MiniLanguage.Types.VariantType import VariantType

    from ...ParserInfos.Common.CapturedVariablesParserInfo import CapturedVariablesParserInfo
    from ...ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo, ConstraintArgumentParserInfo
    from ...ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo, ConstraintParameterParserInfo
    from ...ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo, FuncArgumentParserInfo
    from ...ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo, FuncParameterParserInfo
    from ...ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo, TemplateDecoratorArgumentParserInfo, TemplateTypeArgumentParserInfo
    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateDecoratorParameterParserInfo, TemplateParametersParserInfo, TemplateTypeParameterParserInfo

    from ...Error import CreateError, Error, ErrorException, Region


# ----------------------------------------------------------------------
DuplicateCompileTimeNameError               = CreateError(
    "The compile-time parameter '{name}' has already been defined",
    name=str,
    prev_region=Region,
)

MismatchedDefaultValueTypeError             = CreateError(
    "The default compile-time value for '{name}' is '{actual_type}' but '{expected_type}' was expected",
    name=str,
    actual_type=str,
    expected_type=str,
    expected_type_region=Region,
)


# ----------------------------------------------------------------------
class CommonMixin(BaseMixin):
    # ----------------------------------------------------------------------
    # |  CapturedVariablesParserInfo
    # ----------------------------------------------------------------------
    def OnCapturedVariablesParserInfo(
        self,
        parser_info: CapturedVariablesParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  ConstraintArgumentsParserInfo
    # ----------------------------------------------------------------------
    def OnConstraintArgumentsParserInfo(
        self,
        parser_info: ConstraintArgumentsParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    def OnConstraintArgumentParserInfo(
        self,
        parser_info: ConstraintArgumentParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  ConstraintParametersParserInfo
    # ----------------------------------------------------------------------
    def OnConstraintParametersParserInfo(
        self,
        parser_info: ConstraintParametersParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    def OnConstraintParameterParserInfo(
        self,
        parser_info: ConstraintParameterParserInfo,
    ):
        # Check for duplicate name
        potential_prev_item = self._compile_time_info.GetItemNoThrow(parser_info.name)
        if not isinstance(potential_prev_item, StateMaintainer.DoesNotExist):
            self._errors.append(
                DuplicateCompileTimeNameError.Create(
                    region=parser_info.regions__.name,
                    name=parser_info.name,
                    prev_region=potential_prev_item.parser_info.regions__.name,
                ),
            )

        self._ProcessParameter(parser_info)

    # ----------------------------------------------------------------------
    # |  FuncArgumentsParserInfo
    # ----------------------------------------------------------------------
    def OnFuncArgumentsParserInfo(
        self,
        parser_info: FuncArgumentsParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    def OnFuncArgumentParserInfo(
        self,
        parser_info: FuncArgumentParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  FuncParametersParserInfo
    # ----------------------------------------------------------------------
    def OnFuncParametersParserInfo(
        self,
        parser_info: FuncParametersParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    def OnFuncParameterParserInfo(
        self,
        parser_info: FuncParameterParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  TemplateArgumentsParserInfo
    # ----------------------------------------------------------------------
    def OnTemplateArgumentsParserInfo(
        self,
        parser_info: TemplateArgumentsParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    def OnTemplateTypeArgumentParserInfo(
        self,
        parser_info: TemplateTypeArgumentParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    def OnTemplateDecoratorArgumentParserInfo(
        self,
        parser_info: TemplateDecoratorArgumentParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    # |  TemplateParametersParserInfo
    # ----------------------------------------------------------------------
    def OnTemplateParametersParserInfo(
        self,
        parser_info: TemplateParametersParserInfo,
    ):
        pass

    # ----------------------------------------------------------------------
    def OnTemplateTypeParameterParserInfo(
        self,
        parser_info: TemplateTypeParameterParserInfo,
    ):
        # Check for duplicate name
        potential_prev_item = self._compile_time_info.GetItemNoThrow(parser_info.name)
        if not isinstance(potential_prev_item, StateMaintainer.DoesNotExist):
            self._errors.append(
                DuplicateCompileTimeNameError.Create(
                    region=parser_info.regions__.name,
                    name=parser_info.name,
                    prev_region=potential_prev_item.parser_info.regions__.name,
                ),
            )

        self._compile_time_info.AddItem(
            parser_info.name,
            CompileTimeVariable(
                CompileTimeTemplateTypeWrapper(),
                parser_info.default_type,
                parser_info,
            ),
        )

    # ----------------------------------------------------------------------
    def OnTemplateDecoratorParameterParserInfo(
        self,
        parser_info: TemplateDecoratorParameterParserInfo,
    ):
        # Check for duplicate name
        potential_prev_item = self._compile_time_info.GetItemNoThrow(parser_info.name)
        if not isinstance(potential_prev_item, StateMaintainer.DoesNotExist):
            self._errors.append(
                DuplicateCompileTimeNameError.Create(
                    region=parser_info.regions__.name,
                    name=parser_info.name,
                    prev_region=potential_prev_item.parser_info.regions__.name,
                ),
            )

        self._ProcessParameter(parser_info)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _ProcessParameter(
        self,
        parser_info: Union[
            ConstraintParameterParserInfo,
            TemplateDecoratorParameterParserInfo,
        ],
    ) -> None:
        parameter_type = self.__class__._ParserInfoTypeToMiniLanguageType(parser_info.type)  # type: ignore  # pylint: disable=protected-access

        default_value_expression = None

        if parser_info.default_value is not None:
            default_value_expression = self.CreateMiniLanguageExpression(parser_info.default_value)  # type: ignore
            if isinstance(default_value_expression, Error):
                self._errors.append(default_value_expression)
            else:
                try:
                    default_value_type = default_value_expression.EvalType()  # type: ignore

                    if (
                        default_value_type.name != parameter_type.name
                        and not isinstance(parameter_type, BooleanType)
                        and not (
                            isinstance(parameter_type, VariantType)
                            and default_value_type in parameter_type
                        )
                    ):
                        self._errors.append(
                            MismatchedDefaultValueTypeError.Create(
                                region=parser_info.default_value.regions__.self__,
                                name=parser_info.name,
                                actual_type=default_value_type.name,
                                expected_type=parameter_type.name,
                                expected_type_region=parser_info.type.regions__.self__,
                            ),
                        )

                except ErrorException as ex:
                    self._errors += ex.errors

        self._compile_time_info.AddItem(
            parser_info.name,
            CompileTimeVariable(parameter_type, default_value_expression, parser_info),
        )
