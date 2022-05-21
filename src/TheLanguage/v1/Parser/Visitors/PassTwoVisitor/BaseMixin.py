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
from typing import List, Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..StateMaintainer import StateMaintainer

    from ..NamespaceInfo import ParsedNamespaceInfo

    from ...Error import CreateError, Error, ErrorException
    from ...Helpers import MiniLanguageHelpers

    from ...ParserInfos.ParserInfo import ParserInfo
    from ...ParserInfos.AggregateParserInfo import AggregateParserInfo

    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import ScopedStatementTrait, StatementParserInfo


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
        state: StateMaintainer[MiniLanguageHelpers.CompileTimeInfo],
        this_namespace: ParsedNamespaceInfo,
    ):
        self._state                                                         = state
        self._namespace_stack: List[ParsedNamespaceInfo]                    = [this_namespace]
        self._errors: List[Error]                                           = []

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
                # TODO: get_namespace_info = False
                # TODO:
                # TODO: # The logic of determining when to traverse namespaces is the same as what is found
                # TODO: # in `PassOneVisitor`.
                # TODO: if isinstance(parser_info, ScopedStatementTrait):
                # TODO:     self._state.PushScope()
                # TODO:     exit_stack.callback(self._state.PopScope)
                # TODO:
                # TODO:     get_namespace_info = not isinstance(parser_info, RootStatementParserInfo)
                # TODO:
                # TODO: elif isinstance(parser_info, StatementParserInfo):
                # TODO:     get_namespace_info = True
                # TODO:
                # TODO: if get_namespace_info:
                # TODO:     namespace_info = self._GetNamespaceInfo(parser_info)
                # TODO:     if namespace_info is not None:
                # TODO:         self._namespace_stack.append(namespace_info)
                # TODO:         exit_stack.callback(self._namespace_stack.pop)

                yield

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    @staticmethod
    @contextmanager
    def OnRootStatementParserInfo(*args, **kwargs):
        yield

    # ----------------------------------------------------------------------
    @contextmanager
    def OnAggregateParserInfo(
        self,
        parser_info: AggregateParserInfo,
    ):
        for parser_info in parser_info.parser_infos:
            parser_info.Accept(self)

        yield

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _GetNamespaceInfo(
        self,
        parser_info: ParserInfo,
    ) -> Optional[ParsedNamespaceInfo]:
        item_name = parser_info.GetNameAndRegion()[0]
        if item_name is None:
            return None

        assert self._namespace_stack
        results = self._namespace_stack[-1].children[item_name]

        if isinstance(results, ParsedNamespaceInfo):
            assert results.parser_info == parser_info
            return results

        for result in results:
            if result.parser_info == parser_info:
                return result

        assert False, parser_info

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
