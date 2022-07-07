# ----------------------------------------------------------------------
# |
# |  CommonMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:17:58
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

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ..NamespaceInfo import ParsedNamespaceInfo, ScopeFlag, VisibilityModifier

    from ...Common import MiniLanguageHelpers
    from ...Error import CreateError, Error, ErrorException

    from ...ParserInfos.ParserInfo import ParserInfoType, VisitResult

    from ...ParserInfos.Common.CapturedVariablesParserInfo import CapturedVariablesParserInfo
    from ...ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ...ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo, ConstraintParameterParserInfo
    from ...ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo
    from ...ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo, FuncParameterParserInfo
    from ...ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo, TemplateArgumentParserInfo
    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo, TemplateDecoratorParameterParserInfo, TemplateTypeParameterParserInfo

    from ...ParserInfos.Expressions.Traits.SimpleExpressionTrait import SimpleExpressionTrait

    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait


# ----------------------------------------------------------------------
InvalidCompileTimeTypeError                 = CreateError(
    "'{type}' is not a valid compile-time type",
)

InvalidDefaultTypeError                     = CreateError(
    "Invalid default expression; '{this_type}' was found but '{type}' was expected",
    type=str,
    this_type=str,
)


# ----------------------------------------------------------------------
class CommonMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnCapturedVariablesParserInfo(*args, **kwargs):
        yield

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
    @staticmethod
    @contextmanager
    def OnConstraintParametersParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnConstraintParameterParserInfo(*args, **kwargs):
        yield

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
    @staticmethod
    @contextmanager
    def OnTemplateArgumentsParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateArgumentParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateParametersParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateTypeParameterParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateDecoratorParameterParserInfo(*args, **kwargs):
        yield
