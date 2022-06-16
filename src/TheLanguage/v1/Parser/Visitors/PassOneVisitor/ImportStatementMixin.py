# ----------------------------------------------------------------------
# |
# |  ImportStatementsMixin.py
# |
# |  David Brownell <db@DavidBrownell.db@DavidBrownell.com>
# |      2022-05-10 13:21:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ImportStatementsMixin object"""

import os

from contextlib import contextmanager
from typing import Callable, cast

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import CreateError, ErrorException
    from ...ParserInfos.ParserInfo import ParserInfoType

    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier
    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportType
    from ...ParserInfos.Statements.RootStatementParserInfo import RootStatementParserInfo


# ----------------------------------------------------------------------
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
class ImportStatementMixin(BaseMixin):
    # ----------------------------------------------------------------------
    @contextmanager
    def OnImportStatementParserInfo(
        self,
        parser_info: ImportStatementParserInfo,
    ):
        assert parser_info.parser_info_type__ == ParserInfoType.Configuration, parser_info.parser_info_type__
        self._FlagAsProcessed(parser_info)

        yield

        # We want to introduce the name into the namespace, but don't yet know
        # what the item refers to. Create a placeholder ParsedNamespaceInfo object
        # and then populate it later. These items will be removed during the
        # postprocessing below, as they should only be available after the import statement.

        assert self._namespace_stack
        parent_namespace = self._namespace_stack[-1]

        self._postprocess_funcs.append(cast(Callable[[], None], lambda: self.__class__._PostprocessImportStatement(parent_namespace, parser_info)))  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _PostprocessImportStatement(
        cls,
        parent_namespace: ParsedNamespaceInfo,
        import_parser_info: ImportStatementParserInfo,
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
                item = cls._PostprocessImportStatement(parent, item.parser_info)

            return ParsedNamespaceInfo(
                parent_namespace,
                item.scope_flag,
                item.parser_info,
                children=item.children,
                visibility=import_parser_info.visibility,
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
                children=child_imports,
                visibility=import_parser_info.visibility,
            )

        else:
            assert False, import_parser_info.import_type  # pragma: no cover

        parent_namespace.children[import_parser_info.name] = new_namespace

        return new_namespace
