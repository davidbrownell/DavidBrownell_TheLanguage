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

from collections import OrderedDict
from contextlib import contextmanager
from typing import Callable, cast, Dict, List, Optional

import CommonEnvironment
from CommonEnvironment.DoesNotExist import DoesNotExist

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .BaseMixin import BaseMixin

    from ...Error import CreateError, Error, ErrorException, Region
    from ...NamespaceInfo import NamespaceInfo, ParsedNamespaceInfo

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
    "The import item '{name}' exists but is not visible to the caller",
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
        # postprocessing below.

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

        yield

        self._postprocess_funcs.append(lambda: self.__class__._PostprocessImportStatement(parent_namespace, parser_info))  # pylint: disable=protected-access

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _PostprocessImportStatement(
        cls,
        parent_namespace: ParsedNamespaceInfo,
        parser_info: ImportStatementParserInfo,
    ) -> BaseMixin.PostprocessFuncResultType:
        # ----------------------------------------------------------------------
        def RemoveTemporaryNamespaceItem(
            import_name: str,
        ) -> ParsedNamespaceInfo:
            assert import_name in parent_namespace.children
            assert isinstance(parent_namespace.children[import_name], ParsedNamespaceInfo)

            return cast(ParsedNamespaceInfo, parent_namespace.children.pop(import_name))

        # ----------------------------------------------------------------------
        def FinalizeImports():
            import_items: Dict[str, ParsedNamespaceInfo] = OrderedDict()

            for item_parser_info in parser_info.import_items:
                item_name = item_parser_info.GetNameAndRegion()[0]
                assert item_name is not None

                import_items[item_name] = RemoveTemporaryNamespaceItem(item_name)

            parser_info.InitImports(import_items)

        # ----------------------------------------------------------------------

        # Imports are relative to the file, so find the root namespace of this file (and then
        # jump up a level).
        root_namespace = parser_info.namespace__.parent

        while (
            isinstance(root_namespace, ParsedNamespaceInfo)
            and not isinstance(root_namespace.parser_info, RootParserInfo)
        ):
            root_namespace = root_namespace.parent

        assert isinstance(root_namespace, ParsedNamespaceInfo)
        assert isinstance(root_namespace.parser_info, RootParserInfo)

        root_namespace = root_namespace.parent
        assert isinstance(root_namespace, NamespaceInfo)

        # Get the namespace for the item(s) being imported
        import_namespace = root_namespace

        for source_part in parser_info.source_parts:
            potential_import_namespace = import_namespace.children.get(source_part, DoesNotExist.instance)

            if (
                potential_import_namespace is DoesNotExist.instance
                or isinstance(potential_import_namespace, list)
            ):
                raise ErrorException(
                    ImportModuleNotFoundError.Create(
                        region=parser_info.regions__.source_parts,
                        name=source_part,
                    ),
                )

            assert isinstance(potential_import_namespace, NamespaceInfo)
            import_namespace = potential_import_namespace

        # Get all the items to import
        errors: List[Error] = []

        if parser_info.import_type == ImportType.source_is_directory:
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
                        and hasattr(child_namespace.parser_info, "visibility")
                        and (
                            child_namespace.parser_info.visibility == VisibilityModifier.public  # type: ignore
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
                    parent_namespace,
                    parent_namespace.scope_flag,
                    import_item,
                    child_imports,
                )

            # ----------------------------------------------------------------------

            process_import_item_func = ProcessDirectoryImport

        elif parser_info.import_type == ImportType.source_is_module:
            # ----------------------------------------------------------------------
            def ProcessModuleImport(
                import_item: ImportStatementItemParserInfo,
                import_item_namespace: ParsedNamespaceInfo,
            ) -> Optional[ParsedNamespaceInfo]:
                # TODO: In the future rewrite, all things that are exportable should have name and visibility attributes
                assert hasattr(import_item_namespace.parser_info, "visibility")

                if (
                    import_item_namespace.parser_info.visibility != VisibilityModifier.public  # type: ignore
                    # TODO: Internal
                ):
                    errors.append(
                        ImportItemVisibilityError.Create(
                            region=import_item.regions__.name,
                            name=import_item.name,
                            visibility=import_item_namespace.parser_info.visibility,  # type: ignore
                            visibility_region=import_item_namespace.parser_info.regions__.visibility,
                        ),
                    )

                    return None

                return import_item_namespace

            # ----------------------------------------------------------------------

            process_import_item_func = ProcessModuleImport

        else:
            assert False, parser_info.import_type  # pragma: no cover

        callback_funcs: BaseMixin.PostprocessFuncsType = []
        deferred_count = 0

        for import_item in parser_info.import_items:
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

            import_item_name = import_item.GetNameAndRegion()[0]
            assert import_item_name is not None

            import_item_namespace = process_import_item_func(import_item, import_item_namespace)
            if import_item_namespace is None:
                # Something went wrong, remove this item from the list
                RemoveTemporaryNamespaceItem(import_item_name)
                continue

            if isinstance(import_item_namespace.parser_info, ImportStatementItemParserInfo):
                deferred_count += 1

                # ----------------------------------------------------------------------
                def CallbackFuncFactory(
                    import_item_name: str=import_item_name,
                    import_item=import_item,
                ) -> Callable[[], BaseMixin.PostprocessFuncResultType]:
                    # Create a function that can be called repeatedly for this set of inputs
                    impl = None

                    # ----------------------------------------------------------------------
                    def Impl() -> BaseMixin.PostprocessFuncResultType:
                        import_item_namespace = import_namespace.children[import_item.name]
                        assert isinstance(import_item_namespace, ParsedNamespaceInfo)

                        if isinstance(import_item_namespace.parser_info, ImportStatementItemParserInfo):
                            assert impl is not None
                            return [impl, ]

                        parent_namespace.children[import_item_name] = import_item_namespace

                        nonlocal deferred_count
                        assert deferred_count
                        deferred_count -= 1

                        if deferred_count == 0:
                            return FinalizeImports

                        return None

                    # ----------------------------------------------------------------------

                    impl = Impl
                    return impl

                # ----------------------------------------------------------------------

                callback_funcs.append(CallbackFuncFactory())

            else:
                parent_namespace.children[import_item_name] = import_item_namespace

        if errors:
            raise ErrorException(*errors)

        return callback_funcs or FinalizeImports
