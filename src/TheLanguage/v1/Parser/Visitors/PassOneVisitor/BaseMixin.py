# ----------------------------------------------------------------------
# |
# |  BaseMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-10 13:20:22
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
from typing import Callable, cast, Dict, List, Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Error import CreateError, Error, ErrorException, Region
    from ...Helpers import MiniLanguageHelpers
    from ...NamespaceInfo import ParsedNamespaceInfo

    from ...ParserInfos.ParserInfo import ParserInfo, RootParserInfo, VisitResult

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import ScopeFlag, StatementParserInfo


# ----------------------------------------------------------------------
UnexpectedStatementError                    = CreateError(
    "The statement is not expected at this scope",
    # In the rewrite, give PhraseInfo objects names so that we can identify the statement by name in this error
)

DuplicateNameError                          = CreateError(
    "'{name}' already exists",
    name=str,
    prev_region=Region,
)


# ----------------------------------------------------------------------
class BaseMixin(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    PostprocessFuncResultType               = Union[
        Callable[[], None],                             # Function to call when all files have completed
        "BaseMixin.PostprocessFuncsType",               # Execute additional work
        None,
    ]

    PostprocessFuncsType                    = List[
        Callable[[], "BaseMixin.PostprocessFuncResultType"],
    ]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        configuration_info: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
    ):
        self._configuration_info            = configuration_info

        self._errors: List[Error]                                           = []
        self._postprocess_funcs: BaseMixin.PostprocessFuncsType             = []

        self._namespace_infos: List[ParsedNamespaceInfo]                    = []
        self._root_namespace_info: Optional[ParsedNamespaceInfo]            = None

    # ----------------------------------------------------------------------
    @property
    def errors(self) -> List[Error]:
        assert not self._namespace_infos, self._namespace_infos
        assert self._root_namespace_info is not None
        return self._errors

    @property
    def postprocess_funcs(self) -> "BaseMixin.PostprocessFuncsType":
        assert not self._namespace_infos, self._namespace_infos
        assert self._root_namespace_info is not None
        return self._postprocess_funcs

    @property
    def namespace_info(self) -> ParsedNamespaceInfo:
        assert not self._namespace_infos, self._namespace_infos
        assert self._root_namespace_info is not None
        return self._root_namespace_info

    # ----------------------------------------------------------------------
    def __getattr__(
        self,
        name: str,
    ):
        if name.endswith("ParserInfo"):
            return self.__class__._DefaultParserInfoMethod  # pylint: disable=protected-access

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
        parent_scope_flag = self._namespace_infos[-1].scope_flag if self._namespace_infos else ScopeFlag.Root

        if isinstance(parser_info, StatementParserInfo):
            if (
                (parent_scope_flag == ScopeFlag.Root and not parser_info.scope_flags & ScopeFlag.Root)
                or (parent_scope_flag == ScopeFlag.Class and not parser_info.scope_flags & ScopeFlag.Class)
                or (parent_scope_flag == ScopeFlag.Function and not parser_info.scope_flags & ScopeFlag.Function)
            ):
                self._errors.append(
                    UnexpectedStatementError.Create(
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
                    if isinstance(parser_info, ClassStatementParserInfo):
                        this_scope_flag = ScopeFlag.Class
                    elif isinstance(parser_info, (FuncDefinitionStatementParserInfo, SpecialMethodStatementParserInfo)):
                        this_scope_flag = ScopeFlag.Function
                    else:
                        this_scope_flag = parent_scope_flag

                    new_namespace_info = ParsedNamespaceInfo(
                        self._namespace_infos[-1] if self._namespace_infos else None,
                        this_scope_flag,
                        parser_info,
                    )

                    if isinstance(parser_info, RootParserInfo):
                        assert self._root_namespace_info is None
                        self._root_namespace_info = new_namespace_info

                        assert not self._namespace_infos, self._namespace_infos

                    else:
                        self._AddNamespaceItem(new_namespace_info)

                    self._namespace_infos.append(new_namespace_info)
                    exit_stack.callback(self._namespace_infos.pop)

                elif isinstance(parser_info, StatementParserInfo):
                    assert self._namespace_infos

                    self._AddNamespaceItem(
                        ParsedNamespaceInfo(
                            self._namespace_infos[-1],
                            self._namespace_infos[-1].scope_flag,
                            parser_info,
                        ),
                    )

                yield

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    @classmethod
    def ExecutePostprocessFuncs(
        cls,
        postprocess_funcs: Dict[str, "BaseMixin.PostprocessFuncsType"],
    ) -> Dict[str, List[Error]]:
        errors: Dict[str, List[Error]] = {}
        close_funcs: Dict[str, List[Callable[[], None]]] = {}

        while postprocess_funcs:
            new_postprocess_funcs: Dict[str, BaseMixin.PostprocessFuncsType] = {}

            for name, these_postprocess_funcs in postprocess_funcs.items():
                these_new_postprocess_funcs: BaseMixin.PostprocessFuncsType = []
                these_close_funcs: List[Callable[[], None]] = []
                these_errors: List[Error] = []

                for postprocess_func in these_postprocess_funcs:
                    try:
                        func_result = postprocess_func()

                        if func_result is None:
                            # Nothing to do here
                            pass
                        elif isinstance(func_result, list):
                            these_new_postprocess_funcs += func_result
                        else:
                            these_close_funcs.append(func_result)

                    except ErrorException as ex:
                        these_errors += ex.errors

                if these_new_postprocess_funcs:
                    new_postprocess_funcs.setdefault(name, []).extend(these_new_postprocess_funcs)
                if these_close_funcs:
                    close_funcs.setdefault(name, []).extend(these_close_funcs)
                if these_errors:
                    errors.setdefault(name, []).extend(these_errors)

            postprocess_funcs = new_postprocess_funcs

        # Run all the closing funcs
        for name, these_close_funcs in close_funcs.items():
            these_errors: List[Error] = []

            for close_func in these_close_funcs:
                try:
                    close_func()
                except ErrorException as ex:
                    these_errors += ex.errors

            if these_errors:
                errors.setdefault(name, []).extend(these_errors)

        return errors

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
    def _AddNamespaceItem(
        self,
        namespace: ParsedNamespaceInfo,
    ) -> None:
        item_name, item_name_region = namespace.parser_info.GetNameAndRegion()

        if item_name is not None:
            assert self._namespace_infos

            prev_item = self._namespace_infos[-1].GetScopedNamespaceInfo(item_name)
            if prev_item is not None:
                assert isinstance(prev_item, ParsedNamespaceInfo)

                if (
                    # Does this new item allow for duplicated names?
                    not getattr(namespace.parser_info, "allow_duplicate_named_items__", False)

                    # Do the previous items allow for duplicated names?
                    or (isinstance(prev_item, list) and not getattr(cast(ParsedNamespaceInfo, prev_item[0]).parser_info, "allow_duplicate_named_items__", False))
                    or (isinstance(prev_item, ParsedNamespaceInfo) and not getattr(prev_item.parser_info, "allow_duplicate_named_items__", False))
                ):
                    self._errors.append(
                        DuplicateNameError.Create(
                            region=item_name_region,
                            name=item_name,
                            prev_region=prev_item.parser_info.GetNameAndRegion()[1],
                        ),
                    )

        self._namespace_infos[-1].AddChild(item_name, namespace)
        namespace.parser_info.InitNamespace(namespace)

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
    @staticmethod
    @contextmanager
    def _DefaultParserInfoMethod(*args, **kwargs):  # pylint: disable=unused-argument
        yield

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
