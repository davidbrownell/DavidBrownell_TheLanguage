# ----------------------------------------------------------------------
# |
# |  ImportStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-15 11:10:01
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
from typing import Callable, cast, Dict, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Common import Tokens as CommonTokens

    from ..GrammarStatement import (
        ImportGrammarStatement,
        Leaf,
        MultifileParserObserver,
        Node,
        Statement,
    )

    from ...ParserImpl.MultifileParser import UnknownSourceError


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

    'from' <source> 'import' <content>
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        *file_extensions: str,
    ):
        assert file_extensions

        content_item_statement = [
            # <name> as <name>
            Statement(
                "Renamed",
                CommonTokens.Name,
                CommonTokens.As,
                CommonTokens.Name,
            ),

            # <name>
            CommonTokens.Name,
        ]

        # <content_item_statement> (',' <content_item_statement>)* ','?
        content_items_statement = Statement(
            "Items",
            content_item_statement,
            (
                Statement(
                    "Comma and Item",
                    CommonTokens.Comma,
                    content_item_statement,
                ),
                0,
                None,
            ),
            (CommonTokens.Comma, 0, 1),
        )

        super(ImportStatement, self).__init__(
            # 'from' <name> 'import' ...
            Statement(
                "Import",
                CommonTokens.From,
                CommonTokens.Name,
                CommonTokens.Import,
                [
                    # '(' <content_items_statement> ')'
                    Statement(
                        "Grouped",
                        CommonTokens.LParen,
                        CommonTokens.PushIgnoreWhitespaceControl,
                        content_items_statement,
                        CommonTokens.PopIgnoreWhitespaceControl,
                        CommonTokens.RParen,
                    ),

                    # <content_items_statement>
                    content_items_statement,
                ],
            ),
        )

        self.FileExtensions                 = file_extensions

    # ----------------------------------------------------------------------
    @Interface.override
    def ProcessImportStatement(
        self,
        source_roots: List[str],
        fully_qualified_name: str,
        node: Node,
    ) -> MultifileParserObserver.ImportInfo:

        # We need to get the source and the items to import, however that information depends on
        # context. The content will fall into one of these scenarios:
        #
        #   A) N import items, source is module name; import items are members of the module
        #   B) 1 import item, source is module name; import item is a member of the module
        #   C) 1 import item, source is a directory; import item is a module name

        # Update the source_roots if we are looking at a relative path
        working_dir = os.path.dirname(fully_qualified_name)

        source_leaf = node.Children[1]
        original_source = source_leaf.Value.Match.group("value")

        # The logic applied when looking at all dots is special
        if all(c if c == "." else None for c in original_source):
            original_source_parts = [""] * len(original_source)
        else:
            original_source_parts = original_source.split(".")

        if not original_source_parts[0]:
            # If here, the source started with a dot; the path is relative to the fully_qualified_name
            source_root = os.path.realpath(working_dir)
            original_source_parts.pop(0)

            while original_source_parts and not original_source_parts[0]:
                potential_source_root = os.path.dirname(source_root)

                if potential_source_root == source_root:
                    raise InvalidRelativePathError(
                        source_leaf.IterBefore.Line,
                        source_leaf.IterBefore.Column,
                        original_source,
                        working_dir,
                        source_leaf.IterAfter.Line,
                        source_leaf.IterAfter.Column,
                    )

                source_root = potential_source_root
                original_source_parts.pop(0)

            source_roots = [source_root]

        # Get the items to import
        import_node = node.Children[3]

        # Drill into the Or statement
        assert isinstance(import_node.Type, list)
        assert len(import_node.Children) == 1
        import_node = import_node.Children[0]

        if import_node.Type.Name == "Items":
            import_items, import_items_lookup = self._CreateContentItems(import_node)

        elif import_node.Type.Name == "Grouped":
            # We have to use care when importing the grouped items as we have not yet removed
            # ignored whitespace.
            for child in import_node.Children:
                if isinstance(child.Type, Statement):
                    import_items, import_items_lookup = self._CreateContentItems(child)
                    break

        else:
            assert False, import_node  # pragma: no cover

        # At this point, we have a potential source and items to import. Figure out the scenario
        # that we are in.

        # ----------------------------------------------------------------------
        def FindSource(
            is_valid_root_func: Callable[[str], bool],
            root_suffix: Optional[str]=None,
        ) -> Optional[str]:

            for source_root in source_roots:
                root = os.path.join(source_root, *original_source_parts)
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

        # Check for scenarios A and B
        source_filename = FindSource(lambda name: os.path.isdir(os.path.dirname(name)))

        # Check for scenario C (if necessary)
        if source_filename is None and len(import_items) == 1:
            potential_module_name = next(iter(import_items.keys()))

            source_filename = FindSource(
                os.path.isdir,
                root_suffix=potential_module_name,
            )

        if source_filename is None:
            return MultifileParserObserver.ImportInfo(original_source, None)

        # Cache these values for later
        node.source_filename = source_filename
        node.import_items = import_items
        node.import_items_lookup = import_items_lookup

        return MultifileParserObserver.ImportInfo(original_source, source_filename)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _CreateContentItems(
        cls,
        node: Node,
    ) -> Tuple[
        Dict[str, str],                     # Map of values
        Dict[int, Leaf],                    # Map of strings to tokens
    ]:
        # Get the nodes and ignore the leaves
        nodes = [child for child in node.Children if isinstance(child, Node)]
        assert len(nodes) == 3

        # Extract the import items
        import_items = OrderedDict()
        leaf_lookup = {}

        (
            key,
            key_leaf,
            value,
            value_leaf,
        ) = cls._CreateContentItem(nodes[0])

        import_items[key] = value
        leaf_lookup[id(key)] = key_leaf
        leaf_lookup[id(value)] = value_leaf

        # We can take some liberties here because this functionality is invoked before pruning;
        # therefore, we do not need to determine if we are looking at comma delimited values or
        # just a comma as we do after pruning happens.
        for child in nodes[1].Children:
            for child_node in child.Children:
                if not isinstance(child_node, Node):
                    continue

                (
                    key,
                    key_leaf,
                    value,
                    value_leaf,
                ) = cls._CreateContentItem(child_node)

                import_items[key] = value
                leaf_lookup[id(key)] = key_leaf
                leaf_lookup[id(value)] = value_leaf

                break

        return import_items, leaf_lookup

    # ----------------------------------------------------------------------
    @classmethod
    def _CreateContentItem(
        cls,
        node: Node,
    ) -> Tuple[str, Leaf, str, Leaf]:

        # Drill into the Or Statement
        assert isinstance(node.Type, list)
        assert len(node.Children) == 1
        node = node.Children[0]

        if isinstance(node.Type, Statement):
            # Renamed
            leaves = [cast(Leaf, child) for child in node.Children if isinstance(child, Leaf) and not child.IsIgnored]
            assert len(leaves) == 3

            return (
                leaves[0].Value.Match.group("value"),
                leaves[0],
                leaves[2].Value.Match.group("value"),
                leaves[2],
            )

        elif isinstance(node.Type, CommonTokens.RegexToken):
            leaf = cast(Leaf, node)
            result = leaf.Value.Match.group("value")

            return (result, leaf, result, leaf)
        else:
            assert False, node  # pragma: no cover
