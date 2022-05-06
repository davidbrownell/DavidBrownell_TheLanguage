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

import os

from contextlib import contextmanager
from typing import Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

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
    @staticmethod
    @contextmanager
    def OnCapturedVariablesParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # |  ConstraintArgumentsParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnConstraintArgumentsParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnConstraintArgumentParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # |  ConstraintParametersParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnConstraintParametersParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnConstraintParameterParserInfo(
        self,
        parser_info: ConstraintParameterParserInfo,
    ):
        # Check for duplicate name
        # TODO: potential_prev_item = self._compile_time_info.GetItemNoThrow(parser_info.name)
        # TODO: if not isinstance(potential_prev_item, StateMaintainer.DoesNotExist):
        # TODO:     self._errors.append(
        # TODO:         DuplicateCompileTimeNameError.Create(
        # TODO:             region=parser_info.regions__.name,
        # TODO:             name=parser_info.name,
        # TODO:             prev_region=potential_prev_item.parser_info.regions__.name,
        # TODO:         ),
        # TODO:     )
        # TODO:
        # TODO: self._ProcessParameter(parser_info)

        yield

    # ----------------------------------------------------------------------
    # |  FuncArgumentsParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnFuncArgumentsParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnFuncArgumentParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # |  FuncParametersParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnFuncParametersParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnFuncParameterParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # |  TemplateArgumentsParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateArgumentsParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateTypeArgumentParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateDecoratorArgumentParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # |  TemplateParametersParserInfo
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateParametersParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTemplateTypeParameterParserInfo(
        self,
        parser_info: TemplateTypeParameterParserInfo,
    ):
        # Check for duplicate name
        # TODO: potential_prev_item = self._compile_time_info.GetItemNoThrow(parser_info.name)
        # TODO: if not isinstance(potential_prev_item, StateMaintainer.DoesNotExist):
        # TODO:     self._errors.append(
        # TODO:         DuplicateCompileTimeNameError.Create(
        # TODO:             region=parser_info.regions__.name,
        # TODO:             name=parser_info.name,
        # TODO:             prev_region=potential_prev_item.parser_info.regions__.name,
        # TODO:         ),
        # TODO:     )
        # TODO:
        # TODO: self._compile_time_info.AddItem(
        # TODO:     parser_info.name,
        # TODO:     CompileTimeVariable(
        # TODO:         CompileTimeTemplateTypeWrapper(),
        # TODO:         parser_info.default_type,
        # TODO:         parser_info,
        # TODO:     ),
        # TODO: )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTemplateDecoratorParameterParserInfo(
        self,
        parser_info: TemplateDecoratorParameterParserInfo,
    ):
        # TODO: # Check for duplicate name
        # TODO: potential_prev_item = self._compile_time_info.GetItemNoThrow(parser_info.name)
        # TODO: if not isinstance(potential_prev_item, StateMaintainer.DoesNotExist):
        # TODO:     self._errors.append(
        # TODO:         DuplicateCompileTimeNameError.Create(
        # TODO:             region=parser_info.regions__.name,
        # TODO:             name=parser_info.name,
        # TODO:             prev_region=potential_prev_item.parser_info.regions__.name,
        # TODO:         ),
        # TODO:     )

        self._ProcessParameter(parser_info)

        yield

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
        pass

        # TODO: parameter_type = self.__class__._ParserInfoTypeToMiniLanguageType(parser_info.type)  # type: ignore  # pylint: disable=protected-access
        # TODO:
        # TODO: default_value_expression = None
        # TODO:
        # TODO: if parser_info.default_value is not None:
        # TODO:     default_value_expression = self.CreateMiniLanguageExpression(parser_info.default_value)  # type: ignore
        # TODO:     if isinstance(default_value_expression, Error):
        # TODO:         self._errors.append(default_value_expression)
        # TODO:     else:
        # TODO:         try:
        # TODO:             default_value_type = default_value_expression.EvalType()  # type: ignore
        # TODO:
        # TODO:             if (
        # TODO:                 default_value_type.name != parameter_type.name
        # TODO:                 and not isinstance(parameter_type, BooleanType)
        # TODO:                 and not (
        # TODO:                     isinstance(parameter_type, VariantType)
        # TODO:                     and default_value_type in parameter_type
        # TODO:                 )
        # TODO:             ):
        # TODO:                 self._errors.append(
        # TODO:                     MismatchedDefaultValueTypeError.Create(
        # TODO:                         region=parser_info.default_value.regions__.self__,
        # TODO:                         name=parser_info.name,
        # TODO:                         actual_type=default_value_type.name,
        # TODO:                         expected_type=parameter_type.name,
        # TODO:                         expected_type_region=parser_info.type.regions__.self__,
        # TODO:                     ),
        # TODO:                 )
        # TODO:
        # TODO:         except ErrorException as ex:
        # TODO:             self._errors += ex.errors
        # TODO:
        # TODO: self._compile_time_info.AddItem(
        # TODO:     parser_info.name,
        # TODO:     CompileTimeVariable(parameter_type, default_value_expression, parser_info),
        # TODO: )
