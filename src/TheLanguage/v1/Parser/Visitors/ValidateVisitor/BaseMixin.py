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

from contextlib import contextmanager, ExitStack
from typing import cast, Dict, List, Optional, Union

from dataclasses import dataclass, field

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .StateMaintainer import StateMaintainer

    from ...Error import CreateError, Error, ErrorException
    from ...NamespaceInfo import NamespaceInfo

    from ...Helpers import MiniLanguageHelpers

    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier
    from ...ParserInfos.ParserInfo import ParserInfoType, RootParserInfo, VisitResult

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import ParserInfo, ScopeFlag, StatementParserInfo


# ----------------------------------------------------------------------
UnexpectedStatmentError                     = CreateError(
    "The statement is not expected at this scope",
    # In the rewrite, give PhraseInfo objects names so that we can identify the statement by name in this error
)


# ----------------------------------------------------------------------
class BaseMixin(object):
    """Base class for all mixins associated with this visitor"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        configuration_info: Dict[str, MiniLanguageHelpers.CompileTimeValue],
    ):
        self._configuration_info            = configuration_info

        self._errors: List[Error]                       = []

        self._namespace_infos: List[NamespaceInfo]                          = []
        self._root_namespace_info: Optional[NamespaceInfo]                  = None

    # ----------------------------------------------------------------------
    @property
    def errors(self) -> List[Error]:
        return self._errors

    @property
    def namespaces(self) -> NamespaceInfo:
        assert not self._namespace_infos
        assert self._root_namespace_info

        return self._root_namespace_info

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
        if isinstance(parser_info, StatementParserInfo):
            parent_scope_flag = self._GetParentScopeFlag()

            if (
                (not parser_info.scope_flags & ScopeFlag.Root or parent_scope_flag != ScopeFlag.Root)
                and (not parser_info.scope_flags & ScopeFlag.Class or parent_scope_flag != ScopeFlag.Class)
                and (not parser_info.scope_flags & ScopeFlag.Function or parent_scope_flag != ScopeFlag.Function)
            ):
                self._errors.append(
                    UnexpectedStatmentError.Create(
                        region=parser_info.regions__.self__,
                    ),
                )

                yield VisitResult.SkipAll
                return

        if not self.__class__._GetExecuteFlag(parser_info):  # pylint: disable=protected-access
            yield VisitResult.SkipAll
            return

        try:
            with ExitStack() as exit_stack:
                if parser_info.introduces_scope__:
                    new_namespace_info = NamespaceInfo.Create(parser_info)

                    if isinstance(parser_info, RootParserInfo):
                        assert self._root_namespace_info is None
                        self._root_namespace_info = new_namespace_info

                        assert not self._namespace_infos, self._namespace_infos
                    else:
                        assert self._namespace_infos
                        self._namespace_infos[-1].AddChild(new_namespace_info)

                    self._namespace_infos.append(new_namespace_info)
                    exit_stack.callback(self._namespace_infos.pop)

                    self._PushScope()
                    exit_stack.callback(self._PopScope)

                elif isinstance(parser_info, StatementParserInfo):
                    assert self._namespace_infos
                    self._namespace_infos[-1].AddChild(parser_info)

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
    def _PushScope(self):
        pass # TODO: Update state

    # ----------------------------------------------------------------------
    def _PopScope(self):
        pass # TODO: Update state

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
    def _GetParentScopeFlag(self) -> ScopeFlag:
        for namespace_info in reversed(self._namespace_infos):
            if isinstance(namespace_info.parser_info, ClassStatementParserInfo):
                return ScopeFlag.Class

            if isinstance(namespace_info.parser_info, (FuncDefinitionStatementParserInfo, SpecialMethodStatementParserInfo)):
                return ScopeFlag.Function

        return ScopeFlag.Root

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
