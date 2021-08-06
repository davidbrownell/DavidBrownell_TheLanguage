# ----------------------------------------------------------------------
# |
# |  ImportStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-07-17 09:36:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ImportStatement object"""

import os

from collections import OrderedDict
from enum import auto, Enum
from typing import cast, Callable, Dict, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common.GrammarAST import Leaf, Node

    from ..Common import GrammarDSL
    from ..Common import Tokens as CommonTokens
    from ...GrammarStatement import ImportGrammarStatement
    from ....Statements import StatementDSL

    from ....TranslationUnitsParser import (
        Observer as TranslationUnitsParserObserver,
        UnknownSourceError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidRelativePathError(UnknownSourceError):
    OriginName: str
    LineEnd: int
    ColumnEnd: int

    MessageTemplate                         = Interface.DerivedProperty("The relative path '{SourceName}' is not valid for the origin '{OriginName}'")


# ----------------------------------------------------------------------
class ImportStatement(ImportGrammarStatement):
    """\
    Imports content from another source file.

    'from' <source_file|source_path> 'import' <content>
    """

    NODE_NAME                               = "Import"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class ImportType(Enum):
        SourceIsModule                      = auto()
        SourceIsDirectory                   = auto()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class NodeInfo(object):
        ImportType: "ImportStatement.ImportType"
        SourceFilename: str
        ImportItems: Dict[str, str]
        ImportItemsLookup: Dict[int, Leaf]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *file_extensions: str,
    ):
        assert file_extensions

        # <content_item_statement> (',' <content_item_statement>)* ','?
        content_items_statement = GrammarDSL.CreateDelimitedStatementItem(
            GrammarDSL.StatementItem(
                name="Content Item",
                item=(
                    # <name> 'as' <name>
                    [
                        CommonTokens.Name,
                        CommonTokens.As,
                        CommonTokens.Name,
                    ],

                    # <name>
                    CommonTokens.Name,
                ),
            ),
        )

        super(ImportStatement, self).__init__(
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    # 'from'
                    CommonTokens.From,

                    # <name>
                    CommonTokens.Name,

                    # 'import'
                    CommonTokens.Import,

                    # Content Items
                    (
                        GrammarDSL.StatementItem(
                            name="Grouped",
                            item=[
                                # '('
                                CommonTokens.LParen,
                                CommonTokens.PushIgnoreWhitespaceControl,

                                # <content_items_statement>
                                content_items_statement,

                                # ')'
                                CommonTokens.PopIgnoreWhitespaceControl,
                                CommonTokens.RParen,
                            ],
                        ),

                        # <content_items_statement>
                        content_items_statement,
                    ),

                    CommonTokens.Newline,
                ],
            ),
        )

        self.FileExtensions                 = list(file_extensions)

    # ----------------------------------------------------------------------
    @Interface.override
    def ProcessImportStatement(
        self,
        source_roots: List[str],
        fully_qualified_name: str,
        node: Node,
    ) -> TranslationUnitsParserObserver.ImportInfo:

        assert fully_qualified_name

        (
            raw_source,
            raw_items,
            raw_leaf_lookup,
        ) = self._ExtractRawInfo(node)

        # We need to get the source and the items to import, however that information depends on
        # context. The content will fall into one of these scenarios:
        #
        #   A) N import items, source is module name; import items are members of the module
        #   B) 1 import item, source is module name; import item is a member of the module
        #   C) 1 import item, source is a directory; import item is a module name

        # Update the source_roots if we are looking at a relative path
        working_dir = os.path.dirname(fully_qualified_name)

        # The all does scenario is special
        if all(char if char == "." else None for char in raw_source):
            importing_source_parts = [""] * len(raw_source)
        else:
            importing_source_parts = raw_source.split(".")

        assert importing_source_parts

        # Process relative path info (if any)
        if not importing_source_parts[0]:
            importing_root = os.path.realpath(working_dir)
            importing_source_parts.pop(0)

            while importing_source_parts and not importing_source_parts[0]:
                potential_importing_root = os.path.dirname(importing_root)

                if potential_importing_root == importing_root:
                    source_leaf = raw_leaf_lookup[id(raw_source)]

                    raise InvalidRelativePathError(
                        source_leaf.IterBefore.Line,
                        source_leaf.IterBefore.Column,
                        raw_source,
                        working_dir,
                        source_leaf.IterAfter.Line,
                        source_leaf.IterAfter.Column,
                    )

                importing_root = potential_importing_root
                importing_source_parts.pop(0)

            source_roots = [importing_root]

        # Figure out which scenario we are looking at

        # ----------------------------------------------------------------------
        def FindSource(
            is_valid_root_func: Callable[[str], bool],
            root_suffix: Optional[str]=None,
        ) -> Optional[str]:

            for source_root in source_roots:
                root = os.path.join(source_root, *importing_source_parts)
                if not is_valid_root_func(root):
                    continue

                if root_suffix:
                    root = os.path.join(root, root_suffix)

                for file_extension in self.FileExtensions:
                    potential_filename = root + file_extension
                    if os.path.isfile(potential_filename):
                        return potential_filename

            return None

        # ----------------------------------------------------------------------

        import_type = None

        source_filename = FindSource(lambda name: os.path.isdir(os.path.dirname(name)))
        if source_filename is not None:
            import_type = self.__class__.ImportType.SourceIsModule
        elif len(raw_items) == 1:
            potential_module_name = next(iter(raw_items.keys()))

            source_filename = FindSource(
                os.path.isdir,
                root_suffix=potential_module_name,
            )

            if source_filename is not None:
                import_type = self.__class__.ImportType.SourceIsDirectory

        if source_filename is None:
            return TranslationUnitsParserObserver.ImportInfo(raw_source, None)

        assert import_type is not None

        # Cache the value for later
        object.__setattr__(
            node,
            "Info",
            ImportStatement.NodeInfo(
                import_type,
                source_filename,
                raw_items,
                raw_leaf_lookup,
            ),
        )

        return TranslationUnitsParserObserver.ImportInfo(raw_source, source_filename)

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @staticmethod
    def _ExtractRawInfo(
        node: Node,
    ) -> Tuple[str, Dict[str, str], Dict[int, Leaf]]:

        node_values = StatementDSL.ExtractValues(node)
        leaf_lookup = {}

        # <source>
        source, source_leaf = node_values[1]  # type: ignore
        leaf_lookup[id(source)] = source_leaf

        # Content items
        content_item_values = StatementDSL.ExtractValues(node_values[3])  # type: ignore

        if node_values[3].Type.Name == "Grouped":  # type: ignore
            content_item_values = content_item_values[2]  # type: ignore

        items = OrderedDict()

        for content_item in GrammarDSL.ExtractDelimitedNodeValues(content_item_values):  # type: ignore
            if GrammarDSL.IsLeafValue(content_item):
                key_text, key_leaf = content_item  # type: ignore

                value_text = key_text
                value_leaf = key_leaf

            else:
                content_item = StatementDSL.ExtractValues(content_item)  # type: ignore

                key_text, key_leaf = content_item[0]  # type: ignore
                value_text, value_leaf = content_item[2]  # type: ignore

            items[key_text] = value_text
            leaf_lookup[id(key_text)] = key_leaf
            leaf_lookup[id(value_text)] = value_leaf

        return source, items, leaf_lookup
