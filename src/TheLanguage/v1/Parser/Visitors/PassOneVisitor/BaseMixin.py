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
from typing import Callable, cast, Dict, List, Optional, Set, Tuple, Union

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .. import MiniLanguageHelpers
    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo, VisibilityModifier

    from ...Error import CreateError, Error, ErrorException, TranslationUnitRegion

    from ...ParserInfos.ParserInfo import ParserInfo, ParserInfoType, VisitResult

    from ...ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ...ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ...ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ...ParserInfos.Statements.StatementParserInfo import ScopeFlag, StatementParserInfo

    from ...ParserInfos.Statements.Traits.NamedStatementTrait import NamedStatementTrait
    from ...ParserInfos.Statements.Traits.NewNamespaceScopedStatementTrait import NewNamespaceScopedStatementTrait
    from ...ParserInfos.Statements.Traits.ScopedStatementTrait import ScopedStatementTrait


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
        global_namespace: NamespaceInfo,
        names: Tuple[str, str],
    ):
        self._global_namespace              = global_namespace
        self._configuration_info            = configuration_info
        self._names                         = names

        self._errors: List[Error]                                           = []

        self._postprocess_funcs: List[Callable[[], None]]                   = []
        self._finalize_funcs: List[Callable[[], None]]                      = []

        self._namespace_stack: List[ParsedNamespaceInfo]                    = []
        self._root_namespace: Optional[ParsedNamespaceInfo]                 = None

        self._processed: Set[int]           = set()

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
        parent_scope_flag = self._namespace_stack[-1].scope_flag if self._namespace_stack else ScopeFlag.Root

        if isinstance(parser_info, StatementParserInfo):
            valid_scope_info = parser_info.GetValidScopes().get(parser_info.parser_info_type__, None)

            if valid_scope_info is None or not valid_scope_info & parent_scope_flag:
                self._errors.append(
                    UnexpectedStatementError.Create(
                        region=parser_info.regions__.self__,
                    ),
                )

                yield VisitResult.SkipAll
                return

            # BugBug if (
            # BugBug     (parent_scope_flag == ScopeFlag.Root and not parser_info.scope_flags & ScopeFlag.Root)
            # BugBug     or (parent_scope_flag == ScopeFlag.Class and not parser_info.scope_flags & ScopeFlag.Class)
            # BugBug     or (parent_scope_flag == ScopeFlag.Function and not parser_info.scope_flags & ScopeFlag.Function)
            # BugBug ):
            # BugBug     self._errors.append(
            # BugBug         UnexpectedStatementError.Create(
            # BugBug             region=parser_info.regions__.self__,
            # BugBug         ),
            # BugBug     )
            # BugBug
            # BugBug     yield VisitResult.SkipAll
            # BugBug     return

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
                        self._namespace_stack[-1] if self._namespace_stack else self._global_namespace,
                        scope_flag,
                        cast(StatementParserInfo, parser_info),
                    )

                    try:
                        self._AddNamespaceItem(new_namespace)
                    except ErrorException as ex:
                        self._errors += ex.errors
                        yield VisitResult.SkipAll

                        return

                    if isinstance(parser_info, ScopedStatementTrait):
                        self._namespace_stack.append(new_namespace)
                        exit_stack.callback(self._namespace_stack.pop)

                if isinstance(parser_info, StatementParserInfo):
                    for dynamic_type_name in parser_info.GenerateDynamicTypeNames():
                        assert isinstance(self._namespace_stack[-1], ParsedNamespaceInfo), self._namespace_stack[-1]
                        target_namespace = self._namespace_stack[-1]

                        new_namespace = ParsedNamespaceInfo(
                            target_namespace,
                            ScopeFlag.Class | ScopeFlag.Function,
                            target_namespace.parser_info,
                            name=dynamic_type_name,
                            children=target_namespace.children,
                            visibility=VisibilityModifier.private,
                        )

                        self._AddNamespaceItem(new_namespace)
                yield

                assert parser_info.parser_info_type__ != ParserInfoType.Configuration or id(parser_info) in self._processed, (
                    "Internal Error",
                    parser_info.__class__.__name__,
                )

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
    def _FlagAsProcessed(
        self,
        parser_info: ParserInfo,
    ) -> None:
        key = id(parser_info)

        assert key not in self._processed, key
        self._processed.add(key)

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
            assert self._namespace_stack

            # Is it valid to add this item?

            # Get the ancestor that sets scoping rules, collecting matching names as we go
            matching_namespaces: List[ParsedNamespaceInfo] = []

            ancestor_namespace = self._namespace_stack[-1]

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
                    assert isinstance(matching_namespace.parser_info, NamedStatementTrait), matching_namespace.parser_info
                    if not matching_namespace.parser_info.allow_name_to_be_duplicated__:
                        raise ErrorException(
                            DuplicateNameError.Create(
                                region=new_namespace.parser_info.regions__.name,
                                name=new_namespace.parser_info.name,
                                prev_region=matching_namespace.parser_info.regions__.name,
                            ),
                        )

            # Add it to the parent namespace
            parent_namespace = self._namespace_stack[-1]
            parent_namespace.AddChild(new_namespace)

            if new_namespace.parser_info.name_is_ordered__:
                # ----------------------------------------------------------------------
                def PopChildItem(
                    new_namespace=new_namespace,
                    parent_namespace=parent_namespace,
                ):
                    assert isinstance(new_namespace.parser_info, NamedStatementTrait)
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
        *,
        include_disabled: bool,
    ):
        if isinstance(parser_info_or_infos, list):
            for parser_info in parser_info_or_infos:
                parser_info.Accept(
                    self,
                    include_disabled=include_disabled,
                )
        else:
            parser_info_or_infos.Accept(
                self,
                include_disabled=include_disabled,
            )
