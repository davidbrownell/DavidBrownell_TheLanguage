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

import os
import types

from typing import Any, Dict, List, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StateMaintainer import StateMaintainer

    from ...Error import Error, Warning, Info

    from ...MiniLanguage.Types.Type import Type as MiniLanguageType

    from ...ParserInfos.ParserInfo import ParserInfo, VisitControl
    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo


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
    # ----------------------------------------------------------------------
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
