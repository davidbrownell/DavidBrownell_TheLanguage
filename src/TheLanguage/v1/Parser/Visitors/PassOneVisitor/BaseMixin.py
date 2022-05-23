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
from typing import Callable, Dict, List, Optional, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..NamespaceInfo import ParsedNamespaceInfo

    from ...Error import CreateError, Error, ErrorException, TranslationUnitRegion
    from ...Helpers import MiniLanguageHelpers

    from ...ParserInfos.ParserInfo import ParserInfo, VisitResult

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo

    from ...ParserInfos.Statements.StatementParserInfo import (
        NamedStatementTrait,
        NewNamespaceScopedStatementTrait,
        ScopeFlag,
        ScopedStatementTrait,
        StatementParserInfo,
    )


# ----------------------------------------------------------------------
UnexpectedStatementError                    = CreateError(
    "The statement is not expected at this scope",
    # In the rewrite, give PhraseInfo objects names so that we can identify the statement by name in this error
)

DuplicateNameError                          = CreateError(
    "'{name}' already exists",
    name=str,
    prev_region=TranslationUnitRegion,
)


# ----------------------------------------------------------------------
class BaseMixin(object):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        configuration_info: Dict[str, MiniLanguageHelpers.CompileTimeInfo],
    ):
        self._configuration_info            = configuration_info

        self._errors: List[Error]                                           = []

        self._postprocess_funcs: List[Callable[[], None]]                   = []
        self._finalize_funcs: List[Callable[[], None]]                      = []

        self._namespaces: List[ParsedNamespaceInfo]                         = []
        self._root_namespace: Optional[ParsedNamespaceInfo]                 = None

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
        parent_scope_flag = self._namespaces[-1].scope_flag if self._namespaces else ScopeFlag.Root

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

        try:
            with ExitStack() as exit_stack:
                if isinstance(parser_info, NamedStatementTrait):
                    if isinstance(parser_info, ClassStatementParserInfo):
                        scope_flag = ScopeFlag.Class
                    elif isinstance(parser_info, (FuncDefinitionStatementParserInfo, SpecialMethodStatementParserInfo)):
                        scope_flag = ScopeFlag.Function
                    else:
                        scope_flag = parent_scope_flag

                    new_namespace = ParsedNamespaceInfo(
                        self._namespaces[-1] if self._namespaces else None,
                        scope_flag,
                        parser_info,
                    )

                    try:
                        self._AddNamespaceItem(new_namespace)
                    except ErrorException as ex:
                        self._errors += ex.errors
                        yield VisitResult.SkipAll

                        return

                    if isinstance(parser_info, ScopedStatementTrait):
                        self._namespaces.append(new_namespace)
                        exit_stack.callback(self._namespaces.pop)

                yield

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _AddNamespaceItem(
        self,
        new_namespace_or_namespaces: Union[ParsedNamespaceInfo, List[ParsedNamespaceInfo]],
    ) -> None:
        if isinstance(new_namespace_or_namespaces, list):
            new_namespaces = new_namespace_or_namespaces
        else:
            new_namespaces = [new_namespace_or_namespaces]

        for new_namespace in new_namespaces:
            assert isinstance(new_namespace.parser_info, NamedStatementTrait)

            if isinstance(new_namespace.parser_info, RootStatementParserInfo):
                assert self._root_namespace is None
                self._root_namespace = new_namespace

                continue

            assert self._root_namespace is not None
            assert self._namespaces

            # Is it valid to add this item?

            # Get the ancestor that sets scoping rules, collecting matching names as we go
            matching_namespaces: List[ParsedNamespaceInfo] = []

            ancestor_namespace = self._namespaces[-1]

            while isinstance(ancestor_namespace, ParsedNamespaceInfo):
                potential_matching_namespace = ancestor_namespace.children.get(new_namespace.parser_info.name, None)

                if isinstance(potential_matching_namespace, list):
                    matching_namespaces += potential_matching_namespace
                elif isinstance(potential_matching_namespace, ParsedNamespaceInfo):
                    matching_namespaces.append(potential_matching_namespace)

                if isinstance(ancestor_namespace.parser_info, NewNamespaceScopedStatementTrait):
                    break

                ancestor_namespace = ancestor_namespace.parent

            if matching_namespaces:
                assert isinstance(ancestor_namespace, ParsedNamespaceInfo)
                assert isinstance(ancestor_namespace.parser_info, NewNamespaceScopedStatementTrait)

                if not ancestor_namespace.parser_info.allow_duplicate_names__:
                    raise ErrorException(
                        DuplicateNameError.Create(
                            region=new_namespace.parser_info.regions__.name,
                            name=new_namespace.parser_info.name,
                            prev_region=matching_namespaces[0].parser_info.regions__.name,
                        ),
                    )

                for matching_namespace in matching_namespaces:
                    if not matching_namespace.parser_info.allow_name_to_be_duplicated__:
                        raise ErrorException(
                            DuplicateNameError.Create(
                                region=new_namespace.parser_info.regions__.name,
                                name=new_namespace.parser_info.name,
                                prev_region=matching_namespace.parser_info.regions__.name,
                            ),
                        )

            # Add it to the parent namespace
            parent_namespace = self._namespaces[-1]
            parent_namespace.AddChild(new_namespace)

            if new_namespace.parser_info.name_is_ordered__:
                # ----------------------------------------------------------------------
                def PopChildItem(
                    new_namespace=new_namespace,
                    parent_namespace=parent_namespace,
                ):
                    parent_namespace.children.pop(new_namespace.parser_info.name)

                # ----------------------------------------------------------------------

                self._finalize_funcs.append(PopChildItem)

                assert new_namespace.parser_info.name not in parent_namespace.ordered_children, new_namespace.parser_info.name
                parent_namespace.ordered_children[new_namespace.parser_info.name] = new_namespace

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
