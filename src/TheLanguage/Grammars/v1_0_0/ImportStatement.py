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
    from .Common.GrammarAST import GetRegexMatch, Leaf, Node
    from .Common import GrammarDSL
    from .Common import Tokens as CommonTokens
    from ..GrammarStatement import ImportGrammarStatement

    from ...ParserImpl.Statements.OrStatement import OrStatement
    from ...ParserImpl.Statements.SequenceStatement import SequenceStatement
    from ...ParserImpl.Token import Token

    from ...ParserImpl.TranslationUnitsParser import (
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
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        *file_extensions: str,
    ):
        assert file_extensions

        content_item_statement = (
            # <name> as <name>
            [
                CommonTokens.Name,
                CommonTokens.As,
                CommonTokens.Name,
            ],

            # <name>
            CommonTokens.Name,
        )

        # <content_item_statement> (',' <content_item_statement>)* ','?
        content_items_statement = [
            content_item_statement,
            GrammarDSL.StatementItem(
                Item=[  # type: ignore
                    CommonTokens.Comma,
                    content_item_statement,
                ],
                Arity="*",
            ),
            GrammarDSL.StatementItem(
                Item=CommonTokens.Comma,
                Arity="?",
            ),
        ]

        super(ImportStatement, self).__init__(
            GrammarDSL.CreateStatement(
                name=self.NODE_NAME,
                item=[
                    # 'from' <name> 'import' ...
                    CommonTokens.From,
                    CommonTokens.Name,
                    CommonTokens.Import,
                    (
                        # '(' <content_items_statement> ')'
                        GrammarDSL.StatementItem(
                            Name="Grouped",
                            Item=[
                                CommonTokens.LParen,
                                CommonTokens.PushIgnoreWhitespaceControl,
                                content_items_statement,
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

        # We need to get the source and the items to import, however that information depends on
        # context. The content will fall into one of these scenarios:
        #
        #   A) N import items, source is module name; import items are members of the module
        #   B) 1 import item, source is module name; import item is a member of the module
        #   C) 1 import item, source is a directory; import item is a module name

        # Update the source_roots if we are looking at a relative path
        working_dir = os.path.dirname(fully_qualified_name)

        # Get the source
        source_leaf = cast(Leaf, node.Children[1])
        importing_source = cast(str, GetRegexMatch(source_leaf))

        # Handle the all dots scenario specifically
        if all(character if character == "." else None for character in importing_source):
            importing_source_parts = [""] * len(importing_source)
        else:
            importing_source_parts = importing_source.split(".")

        assert importing_source_parts

        if not importing_source_parts[0]:
            # If here, the importing source started with a dot; the path is relative to the
            # fully_qualified_name
            importing_root = os.path.realpath(working_dir)
            importing_source_parts.pop(0)

            while importing_source_parts and not importing_source_parts[0]:
                potential_importing_root = os.path.dirname(importing_root)

                if potential_importing_root == importing_root:
                    raise InvalidRelativePathError(
                        source_leaf.IterBefore.Line,
                        source_leaf.IterBefore.Column,
                        importing_source,
                        working_dir,
                        source_leaf.IterAfter.Line,
                        source_leaf.IterAfter.Column,
                    )

                importing_root = potential_importing_root
                importing_source_parts.pop(0)

            source_roots = [importing_root]

        # Get the items to import
        items_node = cast(GrammarDSL.Node, node.Children[3])

        # Drill into the Or Node
        assert isinstance(items_node.Type, OrStatement)
        assert len(items_node.Children) == 1
        items_node = cast(GrammarDSL.Node, items_node.Children[0])

        import_items = None
        import_items_lookup = None

        assert items_node.Type

        if items_node.Type.Name == "Grouped":
            # This code is invoked before ignore content is pruned, so we need to
            # account for random whitespace.
            for child_node in items_node.Children:
                if isinstance(child_node.Type, SequenceStatement):
                    import_items, import_items_lookup = self._ExtractImportItems(cast(Node, child_node))
                    break
        else:
            import_items, import_items_lookup = self._ExtractImportItems(items_node)

        # At this point, we have a potential source and items to import. Figure the scenario
        # that we are in.
        assert import_items
        assert import_items_lookup

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
        elif len(import_items) == 1:
            potential_module_name = next(iter(import_items.keys()))

            source_filename = FindSource(
                os.path.isdir,
                root_suffix=potential_module_name,
            )

            if source_filename is not None:
                import_type = self.__class__.ImportType.SourceIsDirectory

        if source_filename is None:
            return TranslationUnitsParserObserver.ImportInfo(importing_source, None)

        assert import_type

        # Cache the values for later
        object.__setattr__(node, "import_type", import_type)
        object.__setattr__(node, "import_items", import_items)
        object.__setattr__(node, "import_items_lookup", import_items_lookup)
        object.__setattr__(node, "source_filename", source_filename)

        return TranslationUnitsParserObserver.ImportInfo(importing_source, source_filename)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractImportItems(
        cls,
        node: Node,
    ) -> Tuple[
        Dict[str, str],                     # Map of values
        Dict[int, Leaf],         # Map of strings to tokens
    ]:
        assert isinstance(node.Type, SequenceStatement), node

        # Ignore potential whitespace
        nodes = [child_node for child_node in node.Children if isinstance(child_node, Node)]
        assert len(nodes) == 3, nodes

        # Extract the import items
        import_items = OrderedDict()
        leaf_lookup = {}

        (
            key,
            key_leaf,
            value,
            value_leaf,
        ) = cls._ExtractImportItem(nodes[0])

        import_items[key] = value
        leaf_lookup[id(key)] = key_leaf
        leaf_lookup[id(value)] = value_leaf

        # We can take some liberties here because this functionality is invoked before pruning;
        # therefore, we do not need to determine if we are looking at comma delimited values or
        # just a comma as we do after pruning happens.
        for child in nodes[1].Children:
            for child_node in cast(Node, child).Children:
                if not isinstance(child_node, Node):
                    continue

                (
                    key,
                    key_leaf,
                    value,
                    value_leaf,
                ) = cls._ExtractImportItem(child_node)

                import_items[key] = value
                leaf_lookup[id(key)] = key_leaf
                leaf_lookup[id(value)] = value_leaf

                break

        return import_items, leaf_lookup

    # ----------------------------------------------------------------------
    @classmethod
    def _ExtractImportItem(
        cls,
        node: Node,
    ) -> Tuple[str, Leaf, str, Leaf]:

        # Drill into the Or node
        assert isinstance(node.Type, OrStatement)
        assert len(node.Children) == 1
        node = cast(Node, node.Children[0])

        if isinstance(node, Node):
            assert isinstance(node.Type, SequenceStatement), node

            # Renamed
            leaves = [cast(Leaf, child) for child in node.Children if isinstance(child, Leaf) and not child.IsIgnored]
            assert len(leaves) == 3

            return (
                cast(str, GetRegexMatch(leaves[0])),
                leaves[0],
                cast(str, GetRegexMatch(leaves[2])),
                leaves[2],
            )

        elif isinstance(node, Leaf):
            leaf = cast(Leaf, node)
            value = cast(str, GetRegexMatch(leaf))

            return (value, leaf, value, leaf)

        else:
            assert False, node  # pragma: no cover
