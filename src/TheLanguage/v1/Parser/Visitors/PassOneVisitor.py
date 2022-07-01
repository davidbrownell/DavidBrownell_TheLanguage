# ----------------------------------------------------------------------
# |
# |  PassOneVisitor.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-07-01 14:30:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the PassOneVisitor object"""

import os
import threading

from contextlib import contextmanager, ExitStack
from typing import Callable, cast, Dict, Generator, List, Optional, Tuple, Union

from dataclasses import dataclass

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo, VisibilityModifier

    from ..Error import CreateError, Error, ErrorException, TranslationUnitRegion

    from ..ParserInfos.ParserInfo import CompileTimeInfo, ParserInfo, ParserInfoType, VisitResult
    from ..ParserInfos.ParserInfoVisitorHelper import ParserInfoVisitorHelper

    from ..ParserInfos.Statements.ClassStatementParserInfo import ClassStatementParserInfo
    from ..ParserInfos.Statements.FuncDefinitionStatementParserInfo import FuncDefinitionStatementParserInfo
    from ..ParserInfos.Statements.IfStatementParserInfo import IfStatementParserInfo
    from ..ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportType
    from ..ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo
    from ..ParserInfos.Statements.SpecialMethodStatementParserInfo import SpecialMethodStatementParserInfo
    from ..ParserInfos.Statements.StatementParserInfo import ScopeFlag, StatementParserInfo

    from ..ParserInfos.Statements.Traits.NamedStatementTrait import NamedStatementTrait
    from ..ParserInfos.Statements.Traits.NewNamespaceScopedStatementTrait import NewNamespaceScopedStatementTrait
    from ..ParserInfos.Statements.Traits.ScopedStatementTrait import ScopedStatementTrait


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

ImportModuleNotFoundError                   = CreateError(
    "The module '{name}' does not exist",
    name=str,
)

ImportItemNotFoundError                     = CreateError(
    "The import item '{name}' does not exist",
    name=str,
)

ImportItemVisibilityError                   = CreateError(
    "The import item '{name}' exists but is not visible here",
    name=str,
)

ImportNoExportedItemsError                  = CreateError(
    "The module '{name}' does not export any items",
    name=str,
)


# ----------------------------------------------------------------------
class PassOneVisitor(ParserInfoVisitorHelper):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Executor(object):
        # ----------------------------------------------------------------------
        # |  Public Methods
        def __init__(
            self,
            mini_language_configuration_values: Dict[str, CompileTimeInfo],
        ):
            self._mini_language_configuration_values    = mini_language_configuration_values

            self._global_namespace          = NamespaceInfo(None, None)

            self._execute_results_lock      = threading.Lock()
            self._execute_results: Dict[
                str,                        # Workspace name
                Dict[
                    str,                    # Relative path
                    PassOneVisitor.Executor._ExecuteResult,  # pylint: disable=protected-access
                ],
            ]                               = {}

        # ----------------------------------------------------------------------
        @property
        def global_namespace(self) -> NamespaceInfo:
            return self._global_namespace

        # ----------------------------------------------------------------------
        def GenerateFuncs(self) -> Generator[
            Tuple[
                bool,                       # is_parallel
                Callable[
                    [
                        Tuple[str, str],
                        RootStatementParserInfo,
                    ],
                    Union[
                        bool,
                        List[Error],
                    ],
                ],
            ],
            None,
            None,
        ]:
            yield True, self._ExecuteParallel

            # Create a complete namespace
            for workspace_name, workspace_items in self._execute_results.items():
                workspace_namespace = NamespaceInfo(workspace_name, self._global_namespace)

                for relative_path, execute_result in workspace_items.items():
                    name_parts = os.path.splitext(relative_path)[0]
                    name_parts = name_parts.split(".")

                    namespace = workspace_namespace

                    for part in name_parts[:-1]:
                        namespace = namespace.GetOrAddChild(part)

                    namespace.AddChild(name_parts[-1], execute_result.namespace)

                self._global_namespace.AddChild(workspace_name, workspace_namespace)

            # Execute all of the postprocess funcs
            for funcs_attribute in [
                "postprocess_funcs",
                "finalize_funcs",
            ]:
                yield False, lambda names, root: self._ExecuteSequential(funcs_attribute, names, root)  # pylint: disable=cell-var-from-loop

        # ----------------------------------------------------------------------
        # |  Private Types
        @dataclass(frozen=True)
        class _ExecuteResult(object):
            # ----------------------------------------------------------------------
            namespace: NamespaceInfo
            postprocess_funcs: List[Callable[[], None]]
            finalize_funcs: List[Callable[[], None]]

        # ----------------------------------------------------------------------
        # |  Private Methods
        def _ExecuteParallel(
            self,
            names: Tuple[str, str],
            root: RootStatementParserInfo,
        ) -> Union[
            bool,                           # Doesn't matter what the return value is as long as it looks different than List[Error]
            List[Error],
        ]:
            visitor = PassOneVisitor(
                self._mini_language_configuration_values,
                self._global_namespace,
                names,
            )

            root.Accept(visitor)

            if visitor._errors:                 # pylint: disable=protected-access
                return visitor._errors          # pylint: disable=protected-access

            with self._execute_results_lock:
                assert visitor._root_namespace is not None  # pylint: disable=protected-access

                self._execute_results.setdefault(names[0], {})[names[1]] = PassOneVisitor.Executor._ExecuteResult(  # pylint: disable=protected-access
                    visitor._root_namespace,                                                                        # pylint: disable=protected-access
                    visitor._postprocess_funcs,                                                                     # pylint: disable=protected-access
                    visitor._finalize_funcs,                                                                        # pylint: disable=protected-access
                )

            return True

        # ----------------------------------------------------------------------
        def _ExecuteSequential(
            self,
            funcs_attribute_name: str,
            names: Tuple[str, str],
            root: RootStatementParserInfo,  # pylint: disable=unused-argument
        ) -> Union[
            bool,
            List[Error],                    # Doesn't matter what the return value is as long as it looks different than List[Error]
        ]:
            # Don't need to acquire the lock, as we will always be reading the data once
            # we start invoking this functionality.
            execute_results = self._execute_results[names[0]][names[1]]

            errors: List[Error] = []

            for func in getattr(execute_results, funcs_attribute_name):
                try:
                    func()
                except ErrorException as ex:
                    errors += ex.errors

            return errors or True

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        configuration_info: Dict[str, CompileTimeInfo],
        global_namespace: NamespaceInfo,
        names: Tuple[str, str],
    ):
        self._global_namespace              = global_namespace
        self._configuration_info            = configuration_info
        self._names_stack                   = [list(names), ]

        self._errors: List[Error]                                           = []

        self._postprocess_funcs: List[Callable[[], None]]                   = []
        self._finalize_funcs: List[Callable[[], None]]                      = []

        self._namespace_stack: List[ParsedNamespaceInfo]                    = []
        self._root_namespace: Optional[ParsedNamespaceInfo]                 = None

    # ----------------------------------------------------------------------
    @contextmanager
    def OnPhrase(
        self,
        parser_info: ParserInfo,
    ):
        assert parser_info.parser_info_type__ != ParserInfoType.CompileTimeTemporary

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

                        self._names_stack.append(self._names_stack[-1] + [parser_info.name, ])
                        exit_stack.callback(self._names_stack.pop)

                if isinstance(parser_info, StatementParserInfo):
                    for dynamic_type_name in parser_info.GenerateDynamicTypeNames():
                        assert isinstance(self._namespace_stack[-1], ParsedNamespaceInfo), self._namespace_stack[-1]
                        target_namespace = self._namespace_stack[-1]

                        new_namespace = ParsedNamespaceInfo(
                            target_namespace,
                            ScopeFlag.Class | ScopeFlag.Function,
                            target_namespace.parser_info,
                            name=dynamic_type_name,
                            visibility=VisibilityModifier.private,
                            children=target_namespace.children,
                        )

                        self._AddNamespaceItem(new_namespace)

                assert self._names_stack

                with parser_info.InitConfiguration(
                    self._names_stack[-1],
                    self._configuration_info,
                ):
                    yield

                if parser_info.parser_info_type__ == ParserInfoType.Configuration:
                    if isinstance(parser_info, IfStatementParserInfo):
                        self._PostprocessIfStatement(parser_info)

                    elif isinstance(parser_info, ImportStatementParserInfo):
                        assert self._namespace_stack
                        active_namespace = self._namespace_stack[-1]

                        # ----------------------------------------------------------------------
                        def NoReturnValueWrapper():
                            self.__class__._PostprocessImportStatement(parser_info, active_namespace)  # pylint: disable=protected-access

                        # ----------------------------------------------------------------------

                        self._postprocess_funcs.append(NoReturnValueWrapper)

        except ErrorException as ex:
            if isinstance(parser_info, StatementParserInfo):
                self._errors += ex.errors
            else:
                raise

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
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

            if new_namespace.parser_info.IsNameOrdered(parent_namespace.scope_flag):
                # ----------------------------------------------------------------------
                def PopChildItem(
                    new_namespace=new_namespace,
                    parent_namespace=parent_namespace,
                ):
                    assert isinstance(new_namespace.parser_info, NamedStatementTrait)

                    namespace_item = parent_namespace.children.pop(new_namespace.parser_info.name)

                    assert new_namespace.parser_info.name not in parent_namespace.ordered_children, new_namespace.parser_info.name
                    parent_namespace.ordered_children[new_namespace.parser_info.name] = namespace_item

                # ----------------------------------------------------------------------

                self._finalize_funcs.append(PopChildItem)

    # ----------------------------------------------------------------------
    def _PostprocessIfStatement(
        self,
        parser_info: IfStatementParserInfo,
    ) -> None:
        # Get the clause that is enabled (if any)
        enabled_clauses: List[ParserInfo] = []

        # ----------------------------------------------------------------------
        class Visitor(ParserInfoVisitorHelper):
            # ----------------------------------------------------------------------
            @staticmethod
            @contextmanager
            def OnPhrase(
                parser_info: ParserInfo,
            ):
                if isinstance(parser_info, IfStatementParserInfo):
                    yield
                    return

                if not parser_info.is_disabled__:
                    enabled_clauses.append(parser_info)

                yield VisitResult.SkipAll

            # ----------------------------------------------------------------------

        # ----------------------------------------------------------------------

        parser_info.Accept(Visitor())

        assert len(enabled_clauses) <= 1, enabled_clauses

        if not enabled_clauses:
            return

        clause_parser_info = enabled_clauses[0]

        assert self._namespace_stack
        namespace = self._namespace_stack[-1]

        assert isinstance(clause_parser_info, NamedStatementTrait), clause_parser_info
        assert clause_parser_info.name in namespace.children

        clause_namespace = namespace.children[clause_parser_info.name]
        assert isinstance(clause_namespace, ParsedNamespaceInfo), clause_namespace

        for clause_namespace_item in clause_namespace.children.values():
            assert isinstance(clause_namespace_item, ParsedNamespaceInfo), clause_namespace_item
            assert isinstance(clause_namespace_item.parser_info, NamedStatementTrait), clause_namespace_item.parser_info
            assert clause_namespace_item.parser_info.name not in namespace.children, clause_namespace_item.parser_info.name

            namespace.children[clause_namespace_item.parser_info.name] = clause_namespace_item

    # ----------------------------------------------------------------------
    @classmethod
    def _PostprocessImportStatement(
        cls,
        import_parser_info: ImportStatementParserInfo,
        parent_namespace: ParsedNamespaceInfo,
    ) -> ParsedNamespaceInfo:
        # Has this item already been processed? This can happen if another compilation unit
        # with a dependency on this import has already been processed.
        existing_namespace = parent_namespace.children[import_parser_info.name]
        assert isinstance(existing_namespace, ParsedNamespaceInfo)

        if not isinstance(existing_namespace.parser_info, ImportStatementParserInfo):
            return existing_namespace

        # If here, continue with the import process

        # Imports are relative to a file, so find the root namespace of this file
        root_namespace = parent_namespace

        while (
            isinstance(root_namespace, ParsedNamespaceInfo)
            and not isinstance(root_namespace.parser_info, RootStatementParserInfo)
        ):
            root_namespace = root_namespace.parent

        assert isinstance(root_namespace, ParsedNamespaceInfo)
        assert isinstance(root_namespace.parser_info, RootStatementParserInfo)

        # Since imports are relative to this file, jump up one more level
        root_namespace = root_namespace.parent
        assert root_namespace is not None
        assert not isinstance(root_namespace, ParsedNamespaceInfo)

        # Get the namespace for the item(s) being imported
        import_namespace = root_namespace

        for source_part in import_parser_info.source_parts:
            potential_import_namespace = import_namespace.children.get(source_part, None)

            if (
                potential_import_namespace is None
                or isinstance(potential_import_namespace, list)
            ):
                raise ErrorException(
                    ImportModuleNotFoundError.Create(
                        region=import_parser_info.regions__.source_parts,
                        name=source_part,
                    ),
                )

            assert isinstance(potential_import_namespace, NamespaceInfo)
            import_namespace = potential_import_namespace

        assert isinstance(import_namespace, ParsedNamespaceInfo)

        # Get all the items to import

        # ----------------------------------------------------------------------
        def ResolveNamespaceItem(
            item: ParsedNamespaceInfo,
            parent: ParsedNamespaceInfo,
        ) -> ParsedNamespaceInfo:
            if isinstance(item.parser_info, ImportStatementParserInfo) and not item.children:
                item = cls._PostprocessImportStatement(item.parser_info, parent)

            return ParsedNamespaceInfo(
                parent_namespace,
                item.scope_flag,
                item.parser_info,
                visibility=import_parser_info.visibility,
                children=item.children,
            )

        # ----------------------------------------------------------------------

        if import_parser_info.import_type == ImportType.source_is_module:
            item_namespace = import_namespace.children.get(import_parser_info.importing_name, None)

            if (
                item_namespace is None
                or isinstance(item_namespace, list)
            ):
                raise ErrorException(
                    ImportItemNotFoundError.Create(
                        region=import_parser_info.regions__.importing_name,
                        name=import_parser_info.importing_name,
                    ),
                )

            assert isinstance(item_namespace, ParsedNamespaceInfo)

            if (
                item_namespace.visibility != VisibilityModifier.public
                # TODO: internal
            ):
                raise ErrorException(
                    ImportItemVisibilityError.Create(
                        region=import_parser_info.regions__.importing_name,
                        name=import_parser_info.importing_name,
                    ),
                )

            new_namespace = ResolveNamespaceItem(item_namespace, parent_namespace)

        elif import_parser_info.import_type == ImportType.source_is_directory:
            module_namespace = import_namespace.children.get(import_parser_info.importing_name, None)

            if (
                module_namespace is None
                or isinstance(module_namespace, list)
            ):
                raise ErrorException(
                    ImportModuleNotFoundError.Create(
                        region=import_parser_info.regions__.importing_name,
                        name=import_parser_info.importing_name,
                    ),
                )

            assert isinstance(module_namespace, ParsedNamespaceInfo)

            child_imports = {}

            for child_name, child_namespace in module_namespace.children.items():
                if (
                    isinstance(child_namespace, ParsedNamespaceInfo)
                    and (
                        child_namespace.visibility == VisibilityModifier.public
                        # TODO: Internal
                    )
                ):
                    child_imports[child_name] = ResolveNamespaceItem(child_namespace, module_namespace)

            if not child_imports:
                raise ErrorException(
                    ImportNoExportedItemsError.Create(
                        region=import_parser_info.regions__.importing_name,
                        name=import_parser_info.importing_name,
                    ),
                )

            new_namespace = ParsedNamespaceInfo(
                parent_namespace,
                parent_namespace.scope_flag,
                import_parser_info,
                visibility=import_parser_info.visibility,
                children=child_imports,
            )

        else:
            assert False, import_parser_info.import_type  # pragma: no cover

        parent_namespace.children[import_parser_info.name] = new_namespace

        return new_namespace
