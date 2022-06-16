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

    from ...ParserInfos.ParserInfo import ParserInfoType

    from ...ParserInfos.Common.CapturedVariablesParserInfo import CapturedVariablesParserInfo
    from ...ParserInfos.Common.ConstraintArgumentsParserInfo import ConstraintArgumentsParserInfo
    from ...ParserInfos.Common.ConstraintParametersParserInfo import ConstraintParametersParserInfo, ConstraintParameterParserInfo
    from ...ParserInfos.Common.FuncArgumentsParserInfo import FuncArgumentsParserInfo
    from ...ParserInfos.Common.FuncParametersParserInfo import FuncParametersParserInfo, FuncParameterParserInfo
    from ...ParserInfos.Common.TemplateArgumentsParserInfo import TemplateArgumentsParserInfo, TemplateTypeArgumentParserInfo
    from ...ParserInfos.Common.TemplateParametersParserInfo import TemplateParametersParserInfo, TemplateDecoratorParameterParserInfo, TemplateTypeParameterParserInfo


# ----------------------------------------------------------------------
class CommonMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnCapturedVariablesParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnConstraintArgumentsParserInfo(
        self,
        parser_info: ConstraintArgumentsParserInfo,
    ):
        assert parser_info.parser_info_type__ == ParserInfoType.TypeCustomization, parser_info.parser_info_type__
        parser_info.SetValidatedFlag()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnConstraintArgumentParserInfo(
        self,
        parser_info: ConstraintArgumentsParserInfo,
    ):
        assert parser_info.parser_info_type__ == ParserInfoType.TypeCustomization, parser_info.parser_info_type__
        parser_info.SetValidatedFlag()

        # BugBug: Handle name; only valid in special methods
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
    def OnTemplateTypeArgumentParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnTemplateDecoratorArgumentParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTemplateParametersParserInfo(
        self,
        parser_info: TemplateParametersParserInfo,
    ):
        assert parser_info.parser_info_type__ == ParserInfoType.TypeCustomization, parser_info.parser_info_type__
        parser_info.SetValidatedFlag()

        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTemplateTypeParameterParserInfo(
        self,
        parser_info: TemplateTypeParameterParserInfo,
    ):
        assert parser_info.parser_info_type__ == ParserInfoType.TypeCustomization, parser_info.parser_info_type__

        assert self._namespaces_stack
        namespace_stack = self._namespaces_stack[-1]

        assert namespace_stack
        namespace = namespace_stack[-1]

        assert isinstance(namespace, ParsedNamespaceInfo), namespace

        assert parser_info.name not in namespace.children
        namespace.children[parser_info.name] = ParsedNamespaceInfo(
            namespace,
            ScopeFlag.Class | ScopeFlag.Function,
            parser_info,
            children=None,
            name=parser_info.name,
            visibility=VisibilityModifier.private,
        )

        parser_info.SetValidatedFlag()
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnTemplateDecoratorParameterParserInfo(
        self,
        parser_info: TemplateDecoratorParameterParserInfo,
    ):
        assert parser_info.parser_info_type__ == ParserInfoType.TypeCustomization, parser_info.parser_info_type__
        parser_info.SetValidatedFlag()

        yield
