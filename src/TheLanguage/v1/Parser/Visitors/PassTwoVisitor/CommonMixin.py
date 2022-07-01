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
    from ...ParserInfos.ParserInfo import ParserInfoType

    from ...ParserInfos.Common.CapturedVariablesParserInfo import CapturedVariablesParserInfo
    from ...ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ...ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo, ConstraintParameterParserInfo
    from ...ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo
    from ...ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo, FuncParameterParserInfo
    from ...ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo, TemplateArgumentParserInfo
    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo, TemplateDecoratorParameterParserInfo, TemplateTypeParameterParserInfo

    from ...ParserInfos.Statements.Traits.TemplatedStatementTrait import TemplatedStatementTrait


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
    @contextmanager
    def OnConstraintParameterParserInfo(
        self,
        parser_info: ConstraintParameterParserInfo,
    ):
        if parser_info.default_value is not None:
            # This is an expression (not a type), so it won't be automatically validated by the BaseMixin
            result = MiniLanguageHelpers.EvalExpression(
                parser_info.default_value,
                self._compile_time_stack,

            )

            parser_info.default_value.SetResolvedEntity(result)

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
    @contextmanager
    def OnTemplateTypeParameterParserInfo(
        self,
        parser_info: TemplateTypeParameterParserInfo,
    ):
        assert self._namespaces_stack
        namespace_stack = self._namespaces_stack[-1]

        assert namespace_stack
        parent_namespace = namespace_stack[-1]

        assert isinstance(parent_namespace, ParsedNamespaceInfo), parent_namespace
        assert isinstance(parent_namespace.parser_info, TemplatedStatementTrait), parent_namespace.parser_info

        assert parser_info.name not in parent_namespace.children
        parent_namespace.AddChild(
            ParsedNamespaceInfo(
                parent_namespace,
                parent_namespace.scope_flag,
                parser_info,
                name=parser_info.name,
                visibility=VisibilityModifier.private,
            ),
        )

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTemplateDecoratorParameterParserInfo(
        self,
        parser_info: TemplateDecoratorParameterParserInfo,
    ):
        if parser_info.default_value is not None:
            # This is an expression (not a type), so it won't be automatically validated by the BaseMixin
            result = MiniLanguageHelpers.EvalExpression(
                parser_info.default_value,
                self._compile_time_stack,

            )

            parser_info.default_value.SetResolvedEntity(result)

        yield
