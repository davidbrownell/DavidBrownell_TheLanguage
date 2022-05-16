# ----------------------------------------------------------------------
# |
# |  BaseMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-16 10:17:15
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

from contextlib import contextmanager, ExitStack
from typing import Dict, List, Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..StateMaintainer import StateMaintainer

    from ...Error import CreateError, Error, ErrorException
    from ...Helpers import MiniLanguageHelpers
    from ...NamespaceInfo import ParsedNamespaceInfo

    from ...MiniLanguage.Types.CustomType import CustomType

    from ...ParserInfos.ParserInfo import ParserInfo, VisitResult
    from ...ParserInfos.Expressions.ExpressionParserInfo import ExpressionParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import StatementParserInfo


# ----------------------------------------------------------------------
InvalidTypeError                            = CreateError(
    "'{name}' is not a valid type",
    name=str,
)


# ----------------------------------------------------------------------
class BaseMixin(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        configuration_info: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
    ):
        self._state: StateMaintainer[MiniLanguageHelpers.CompileTimeInfo]   = StateMaintainer(configuration_info)

        self._errors: List[Error]           = []

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
        parser_info: ParserInfo,
    ):
        if not self.__class__._GetExecuteFlag(parser_info):  # pylint: disable=protected-access
            yield VisitResult.SkipAll
            return

        try:
            with ExitStack() as exit_stack:
                if parser_info.introduces_scope__:
                    self._state.PushScope()
                    exit_stack.callback(self._state.PopScope)

                yield

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnRootParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _SetExecuteFlag(
        cls,
        statement: ParserInfo,
        value: bool,
    ) -> None:
        object.__setattr__(statement, cls._EXECUTE_STATEMENT_FLAG_ATTTRIBUTE_NAME, value)

    # ----------------------------------------------------------------------
    @classmethod
    def _GetExecuteFlag(
        cls,
        statement: ParserInfo,
    ) -> bool:
        return getattr(statement, cls._EXECUTE_STATEMENT_FLAG_ATTTRIBUTE_NAME, True)

    # ----------------------------------------------------------------------
    def _GetNamespaceInfo(
        self,
        parser_info: ExpressionParserInfo,
        snapshot: Optional[Dict[str, MiniLanguageHelpers.CompileTimeInfo]]=None,
    ) -> ParsedNamespaceInfo:
        snapshot = snapshot or self._state.CreateFlatSnapshot()

        type_result = MiniLanguageHelpers.EvalExpression(parser_info, snapshot)

        type_name = type_result.type.name

        if type_name not in snapshot:
            raise ErrorException(
                InvalidTypeError.Create(
                    region=parser_info.regions__.self__,
                    name=type_name,
                ),
            )

        # TODO: Return ParsedNamespaceInfo
        return type_result.type

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
