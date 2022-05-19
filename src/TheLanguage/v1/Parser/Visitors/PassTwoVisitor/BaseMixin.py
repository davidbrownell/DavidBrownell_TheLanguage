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
    def _GetNamespaceInfo(
        self,
        parser_info: ExpressionParserInfo,
        snapshot: Optional[Dict[str, MiniLanguageHelpers.CompileTimeInfo]]=None,
    ) -> ParsedNamespaceInfo:
        snapshot = snapshot or self._state.CreateFlatSnapshot()

        type_result = MiniLanguageHelpers.EvalExpression(parser_info, snapshot)

        type_name = type_result.type.name
        type_info = snapshot.get(type_name, None)

        if type_info is None:
            raise ErrorException(
                InvalidTypeError.Create(
                    region=parser_info.regions__.self__,
                    name=type_name,
                ),
            )

        return type_info.value

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
