# ----------------------------------------------------------------------
# |
# |  ImportStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-06-06 08:39:25
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains statements that import code from other modules"""

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
    from . import CommonTokens

    from ..GrammarStatement import (
        ImportGrammarStatement,
        Leaf,
        MultifileParserObserver,
        Node,
        Statement,
    )

    from ...ParserImpl.MultifileParser import UnknownSourceError

# TODO: Clean this file up once there are a couple of statements defined so that
#       each are consistent with emerging best practices.

# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidRelativePathError(UnknownSourceError):
    OriginName: str
    LineEnd: int
    ColumnEnd: int

    MessageTemplate                         = Interface.DerivedProperty("The relative path '{SourceName}' is not valid for the origin '{OriginName}'")


# ----------------------------------------------------------------------
class ImportStatement(ImportGrammarStatement):
    """'from' <source> 'import' <content>"""

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
                CommonTokens.NameToken,
                CommonTokens.AsToken,
                CommonTokens.NameToken,
            ),

            # <name>
            CommonTokens.NameToken,
        ]

        # <item_statement> (',' <item_statement>)* ','?
        content_items_statement = Statement(
            "Items",
            content_item_statement,
            (
                Statement(
                    "Comma and Statement",
                    CommonTokens.CommaToken,
                    content_item_statement,
                ),
                0,
                None,
            ),
            (CommonTokens.CommaToken, 0, 1),
        )

        super(ImportStatement, self).__init__(
            # 'from' <name> 'import' ...
            Statement(
                "Import",
                CommonTokens.FromToken,
                CommonTokens.NameToken,
                CommonTokens.ImportToken,
                [
                    # '(' <items_statement> ')'
                    Statement(
                        "Grouped Items",
                        CommonTokens.LParenToken,
                        CommonTokens.PushIgnoreWhitespaceControlToken(),
                        content_items_statement,
                        CommonTokens.PopIgnoreWhitespaceControlToken(),
                        CommonTokens.RParenToken,
                    ),

                    # <items_statement>
                    content_items_statement,
                ],
            ),
        )

        self.FileExtensions                 = file_extensions
        self._content_items_statement       = content_items_statement

    # ----------------------------------------------------------------------
    @Interface.override
    def ProcessImportStatement(
        self,
        source_roots: List[str],
        fully_qualified_name: str,
        node: Node,
    ) -> MultifileParserObserver.ImportInfo:

        working_dir = os.path.dirname(fully_qualified_name)

        # Calculate the
        source_leaf = node.Children[1]
        original_source = source_leaf.Value.Match.group("value")

        # The logic with all dots is slightly different from the standard logic
        if all(c if c == "." else None for c in original_source):
            original_source_parts = [""] * len(original_source)
        else:
            original_source_parts = original_source.split(".")

        if not original_source_parts[0]:
            # If here, the source started with a dot and we are looking at a path relative to
            # the fully qualified name
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

        # Calculate the items to import
        import_result = node.Children[3]

        assert len(import_result.Children) == 1
        import_result = import_result.Children[0]

        if import_result.Type == self._content_items_statement:
            import_items, import_items_lookup = self._ProcessContentItems(import_result)

        elif import_result.Type.Name == "Grouped Items":
            for child in import_result.Children:
                if child.Type == self._content_items_statement:
                    import_items, import_items_lookup = self._ProcessContentItems(child)
                    break

        else:
            assert False, import_result  # pragma: no cover

        # At this point, we don't know if the source points to a directory or
        # a module name. We are in one of these scenarios:
        #
        #   A) N import items, source is module name; import items are members of the module
        #   B) 1 import item, source is module name; import item is a member of the module
        #   C) 1 import item, source is a directory; import item is a module name

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

        # Cache these values for later so we don't need to reparse the content
        node.source_filename = source_filename
        node.import_items = import_items
        node.import_items_lookup = import_items_lookup

        return MultifileParserObserver.ImportInfo(original_source, source_filename)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _ProcessContentItems(
        cls,
        node: Node,
    ) -> Tuple[
            Dict[str, str],                 # Map of values
            Dict[int, Leaf],                # Map of strings to tokens
        ]:
        # Get the nodes (and ignore the leaves)
        nodes = [child for child in node.Children if isinstance(child, Node)]
        assert len(nodes) == 3, nodes

        # Extract the import items
        import_items = OrderedDict()
        leaf_lookup = {}

        (
            key,
            key_leaf,
            value,
            value_leaf,
        ) = cls._ProcessContentItem(nodes[0])

        import_items[key] = value
        leaf_lookup[id(key)] = key_leaf
        leaf_lookup[id(value)] = value_leaf

        for child in nodes[1].Children:
            for child_node in child.Children:
                if not isinstance(child_node, Node):
                    continue

                (
                    key,
                    key_leaf,
                    value,
                    value_leaf,
                ) = cls._ProcessContentItem(child_node)

                import_items[key] = value
                leaf_lookup[id(key)] = key_leaf
                leaf_lookup[id(value)] = value_leaf

                break

        return import_items, leaf_lookup

    # ----------------------------------------------------------------------
    @staticmethod
    def _ProcessContentItem(
        node: Node,
    ) -> Tuple[str, Leaf, str, Leaf]:
        assert len(node.Children) == 1, node
        node = node.Children[0]

        if isinstance(node.Type, Statement):
            leaves = [cast(Leaf, child) for child in node.Children if isinstance(child, Leaf) and not child.IsIgnored]
            assert len(leaves) == 3, leaves

            return (
                leaves[0].Value.Match.group("value"),
                leaves[0],
                leaves[2].Value.Match.group("value"),
                leaves[2],
            )

        elif isinstance(node.Type, CommonTokens.RegexToken):
            result = cast(Leaf, node).Value.Match.group("value")

            return (result, node, result, node)

        else:
            assert False, node.Type  # pragma: no cover
