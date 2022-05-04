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

from contextlib import contextmanager
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

    from ...Error import Error, ErrorException

    from ...Helpers import MiniLanguageHelpers

    from ...MiniLanguage.Types.IntegerType import IntegerType

    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier
    from ...ParserInfos.Statements.StatementParserInfo import ParserInfo, Region, StatementParserInfo


# ----------------------------------------------------------------------
class CompileTimeTemplateTypeWrapper(object):
    pass


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
        configuration_info: Dict[str, MiniLanguageHelpers.CompileTimeValue],
    ):
        self._configuration_info            = configuration_info

        self._errors: List[Error]           = []

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
        index = name.find("ParserInfo__")
        if index != -1 and index + len("ParserInfo__") + 1 < len(name):
            return types.MethodType(self.__class__._DefaultDetailMethod, self)  # pylint: disable=protected-access

        raise AttributeError(name)

    # ----------------------------------------------------------------------
    @contextmanager
    def OnPhrase(
        self,
        parser_info: ParserInfo,  # pylint: disable=unused-argument
    ):
        try:
            yield

            if self._scope_level + self._scope_delta == 1:
                pass # TODO

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    @contextmanager
    def OnNewScope(
        self,
        parser_info: ParserInfo,  # pylint: disable=unused-argument
    ):
        self._PushScope()

        yield

        self._PopScope()

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnRootParserInfo(
        parser_info: ParserInfo,  # pylint: disable=unused-argument
    ):
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _PushScope(self):
        self._scope_level += 1

    # ----------------------------------------------------------------------
    def _PopScope(self):
        assert self._scope_level
        self._scope_level -= 1

    # ----------------------------------------------------------------------
    @classmethod
    def _SetExecuteFlag(
        cls,
        statement: ParserInfo,
        value: bool,
    ):
        object.__setattr__(statement, cls._EXECUTE_STATEMENT_FLAG_ATTTRIBUTE_NAME, value)

    # ----------------------------------------------------------------------
    @classmethod
    def _GetExecuteFlag(
        cls,
        statement: ParserInfo,
    ):
        return getattr(statement, cls._EXECUTE_STATEMENT_FLAG_ATTTRIBUTE_NAME, True)

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _EXECUTE_STATEMENT_FLAG_ATTTRIBUTE_NAME = "_execute_statement"

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
                parser_info.Accept(self)
        else:
            parser_info_or_infos.Accept(self)
