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
import weakref

from collections import OrderedDict
from contextlib import contextmanager
from typing import cast, Dict, List, Optional

import CommonEnvironment
from CommonEnvironment.DoesNotExist import DoesNotExist

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ..NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

    from ...Error import CreateError, Error, ErrorException, Region

    from ...ParserInfos.ParserInfo import RootParserInfo

    from ...ParserInfos.Common.VisibilityModifier import VisibilityModifier

    from ...ParserInfos.Statements.ImportStatementParserInfo import ImportStatementParserInfo, ImportStatementItemParserInfo, ImportType


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
    visibility=VisibilityModifier,
    visibility_region=Region,
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
        # We want to introduce the name into the namespace, but don't yet know
        # what the item refers to. Create a placeholder ParsedNamespaceInfo object
        # and then populate it later. These items will be removed during the
        # postprocessing below, as they should only be available after the import statement.

        assert self._namespace_infos
        parent_namespace = self._namespace_infos[-1]

        for import_item in parser_info.import_items:
            self._AddNamespaceItem(
                ParsedNamespaceInfo(
                    parent_namespace,
                    parent_namespace.scope_flag,
                    import_item,
                ),
            )

            # Associate the parent parser_info with the import item. This will
            # be used later when postprocessing the imports themselves. Note that
            # we can't use the state of this object, as different visitors are created
            # for different compilation units. This information will be removed during
            # finalization.
            object.__setattr__(
                import_item,
                self.__class__._TEMPORARY_IMPORT_ITEM_PARENT_ATTRIBUTE_NAME,  # pylint: disable=protected-access
                weakref.ref(parser_info),
            )

        yield

        self._postprocess_funcs.append(
            (
                lambda: self.__class__._PostprocessImportStatement(parent_namespace, parser_info),  # pylint: disable=protected-access
                lambda: self.__class__._FinalizeImportStatement(parent_namespace, parser_info),  # pylint: disable=protected-access
            ),
        )

    # ----------------------------------------------------------------------
    # |
    # |  Private Data
    # |
    # ----------------------------------------------------------------------
    _TEMPORARY_IMPORT_ITEM_PARENT_ATTRIBUTE_NAME        = "_import_statement_parser_info"

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _PostprocessImportStatement(
        cls,
        namespace: ParsedNamespaceInfo,
        import_statement_parser_info: ImportStatementParserInfo,
    ) -> None:
        # Imports are relative to a file, so find the root namespace of this file
        root_namespace = namespace

        while (
            isinstance(root_namespace, ParsedNamespaceInfo)
            and not isinstance(root_namespace.parser_info, RootParserInfo)
        ):
            root_namespace = root_namespace.parent

        assert isinstance(root_namespace, ParsedNamespaceInfo)
        assert isinstance(root_namespace.parser_info, RootParserInfo)

        # Since imports are relative to this file, jump up one more level
        root_namespace = root_namespace.parent
        assert root_namespace is not None
        assert not isinstance(root_namespace, ParsedNamespaceInfo)

        # Get the namespace for the item(s) being imported
        import_namespace = root_namespace

        for source_part in import_statement_parser_info.source_parts:
            potential_import_namespace = import_namespace.children.get(source_part, DoesNotExist.instance)

            if (
                potential_import_namespace is DoesNotExist.instance
                or isinstance(potential_import_namespace, list)
            ):
                raise ErrorException(
                    ImportModuleNotFoundError.Create(
                        region=import_statement_parser_info.regions__.source_parts,
                        name=source_part,
                    ),
                )

            assert isinstance(potential_import_namespace, NamespaceInfo)
            import_namespace = potential_import_namespace

        assert isinstance(import_namespace, ParsedNamespaceInfo)

        # Get all the items to import
        errors: List[Error] = []

        if import_statement_parser_info.import_type == ImportType.source_is_directory:
            # ----------------------------------------------------------------------
            def ProcessDirectoryImport(
                import_item: ImportStatementItemParserInfo,
                import_item_namespace: ParsedNamespaceInfo,
            ) -> Optional[ParsedNamespaceInfo]:
                # Import everything that is public
                child_imports = OrderedDict()

                for child_name, child_namespace in import_item_namespace.children.items():
                    if (
                        child_name is not None
                        and isinstance(child_namespace, ParsedNamespaceInfo)
                        and (
                            getattr(child_namespace.parser_info, cls._TEMPORARY_IMPORT_ITEM_PARENT_ATTRIBUTE_NAME)().visibility == VisibilityModifier.public  # type: ignore
                            # TODO: Internal
                        )
                    ):
                        child_imports[child_name] = child_namespace

                if not child_imports:
                    errors.append(
                        ImportNoExportedItemsError.Create(
                            region=import_item.regions__.name,
                            name=import_item.name,
                        ),
                    )

                    return None

                return ParsedNamespaceInfo(
                    namespace,
                    namespace.scope_flag,
                    import_item,
                    child_imports,
                )

            # ----------------------------------------------------------------------

            process_import_item_func = ProcessDirectoryImport

        elif import_statement_parser_info.import_type == ImportType.source_is_module:
            # ----------------------------------------------------------------------
            def ProcessModuleImport(
                import_item: ImportStatementItemParserInfo,
                import_item_namespace: ParsedNamespaceInfo,
            ) -> Optional[ParsedNamespaceInfo]:
                # TODO: In the future rewrite, all things that are exportable should have a name and visibility

                imported_item_parser_info = import_item_namespace.parser_info
                if isinstance(imported_item_parser_info, ImportStatementItemParserInfo):
                    imported_item_parser_info = getattr(import_item_namespace.parser_info, cls._TEMPORARY_IMPORT_ITEM_PARENT_ATTRIBUTE_NAME)()

                assert hasattr(imported_item_parser_info, "visibility")

                if (
                    imported_item_parser_info.visibility != VisibilityModifier.public  # type: ignore
                    # TODO: Internal
                ):
                    errors.append(
                        ImportItemVisibilityError.Create(
                            region=import_item.regions__.name,
                            name=import_item.name,
                            visibility=imported_item_parser_info.visibility,  # type: ignore
                            visibility_region=imported_item_parser_info.regions__.visibility,
                        ),
                    )

                    return None

                return import_item_namespace

            # ----------------------------------------------------------------------

            process_import_item_func = ProcessModuleImport

        else:
            assert False, import_statement_parser_info.import_type  # pragma: no cover

        for import_item in import_statement_parser_info.import_items:
            import_item_name = import_item.GetNameAndRegion()[0]
            assert import_item_name is not None

            # Has this item already been processed? This can happen if another compilation unit
            # too a dependency on this import.
            existing_import_item_namespace = namespace.children.get(import_item_name)
            assert isinstance(existing_import_item_namespace, ParsedNamespaceInfo)

            if not isinstance(existing_import_item_namespace.parser_info, ImportStatementItemParserInfo):
                continue

            # If here, continue with the import process
            import_item_namespace = import_namespace.children.get(import_item.name, DoesNotExist.instance)

            if (
                import_item_namespace is DoesNotExist.instance
                or isinstance(import_item_namespace, list)
            ):
                errors.append(
                    ImportItemNotFoundError.Create(
                        region=import_item.regions__.name,
                        name=import_item.name,
                    ),
                )

                continue

            assert isinstance(import_item_namespace, ParsedNamespaceInfo)

            import_item_namespace = process_import_item_func(import_item, import_item_namespace)
            if import_item_namespace is None:
                # Something went wrong and we will not be able to import it
                assert errors
                continue

            if isinstance(import_item_namespace.parser_info, ImportStatementItemParserInfo):
                cls._PostprocessImportStatement(
                    import_namespace,
                    getattr(
                        import_item_namespace.parser_info,
                        cls._TEMPORARY_IMPORT_ITEM_PARENT_ATTRIBUTE_NAME,
                    )(),
                )

                import_item_namespace = import_namespace.children.get(import_item.name)
                assert isinstance(import_item_namespace, ParsedNamespaceInfo)

            namespace.children[import_item_name] = import_item_namespace

        if errors:
            raise ErrorException(*errors)

    # ----------------------------------------------------------------------
    @classmethod
    def _FinalizeImportStatement(
        cls,
        namespace: ParsedNamespaceInfo,
        import_statement_parser_info: ImportStatementParserInfo,
    ) -> None:
        # Commit the results and remove temporary working state

        # ----------------------------------------------------------------------
        def RemoveTemporaryNamespaceItem(
            import_name: str,
        ) -> ParsedNamespaceInfo:
            assert import_name in namespace.children
            assert isinstance(namespace.children[import_name], ParsedNamespaceInfo)

            return cast(ParsedNamespaceInfo, namespace.children.pop(import_name))

        # ----------------------------------------------------------------------

        import_items: Dict[str, ParsedNamespaceInfo] = OrderedDict()

        for item_parser_info in import_statement_parser_info.import_items:
            object.__delattr__(item_parser_info, cls._TEMPORARY_IMPORT_ITEM_PARENT_ATTRIBUTE_NAME)

            item_name = item_parser_info.GetNameAndRegion()[0]
            assert item_name is not None

            import_items[item_name] = RemoveTemporaryNamespaceItem(item_name)

        import_statement_parser_info.InitImports(import_items)
