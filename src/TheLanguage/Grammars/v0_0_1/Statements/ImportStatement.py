# ----------------------------------------------------------------------
# |
# |  ImportStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-14 17:03:04
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

import itertools
import os
import re

from enum import auto, Enum
from typing import Callable, cast, List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import ImportGrammarStatement

    from ....Parser.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
        RegexToken,
    )

    from ....Parser.TranslationUnitsParser import (
        Observer as TranslationUnitsParserObserver,
        UnknownSourceError,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidRelativePathError(UnknownSourceError):
    OriginName: str
    LineEnd: int
    ColumnEnd: int

    MessageTemplate                         = Interface.DerivedProperty(
        "The relative path '{SourceName}' is not valid for the origin '{OriginName}'.",
    )


# ----------------------------------------------------------------------
class ImportStatement(ImportGrammarStatement):
    """\
    Imports content from another file.

    'from' <source_file|source_path> 'import' <content>

    Examples:
        from Module import Foo
        from Module import Bar as _Bar
        from Module2 import Biz, Baz
        from Module.File import A, B, C
    """

    PHRASE_NAME                             = "Import Statement"

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class ImportType(Enum):
        SourceIsModule                      = auto()
        SourceIsDirectory                   = auto()

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class ImportItemInfo(ImportGrammarStatement.NodeInfo):
        Name: str
        Alias: Optional[str]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NodeInfo(ImportGrammarStatement.NodeInfo):
        ImportType: "ImportStatement.ImportType"
        SourceFilename: str
        ImportItems: List["ImportStatement.ImportItemInfo"]

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

        # <name> ('as' <name>)?
        content_item = PhraseItem(
            name="Content Item",
            item=[
                # <name>
                CommonTokens.GenericName,

                # ('as' <name>)?
                PhraseItem(
                    name="Suffix",
                    item=[
                        "as",
                        CommonTokens.GenericName,
                    ],
                    arity="?",
                ),
            ],
        )

        # <content_item> (',' <content_item>)* ','?
        content_items = PhraseItem(
            name="Content Items",
            item=[
                # <content_item>
                content_item,

                # (',' <content_item>)*
                PhraseItem(
                    name="Comma and Content",
                    item=[
                        ",",
                        content_item,
                    ],
                    arity="*",
                ),

                # ','?
                PhraseItem(
                    name="Trailing Comma",
                    item=",",
                    arity="?",
                ),
            ],
        )

        super(ImportStatement, self).__init__(
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # 'from'
                    "from",

                    # <name>: Note that the possibility of a dot-only token means that we can't use
                    #         CommonTokens.GenericName here.
                    RegexToken("<dotted_generic_name>", re.compile(r"(?P<value>[a-zA-Z0-9\._]+)")),

                    # 'import'
                    "import",

                    # Content Items
                    PhraseItem(
                        item=(
                            # '(' <content_items> ')'
                            PhraseItem(
                                name="Grouped",
                                item=[
                                    # '('
                                    "(",
                                    CommonTokens.PushIgnoreWhitespaceControl,

                                    # <content_items>
                                    content_items,

                                    # ')'
                                    CommonTokens.PopIgnoreWhitespaceControl,
                                    ")",
                                ],
                            ),

                            # <content_items>
                            content_items,
                        ),

                        # Use the order to disambiguate between group clauses and tuples.
                        ordered_by_priority=True,
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

        source, source_leaf, import_items = self._ExtractRawInfo(node)

        # We need to get the source and the items to import, however that information depends on
        # context. The content will fall into one of these scenarios:
        #
        #   A) N import items, source is module name; import items are members of the module
        #   B) 1 import item, source is module name; import item is a member of the module
        #   C) 1 import item, source is a directory; import item is a module name

        # Update the source_roots if we are looking at a relative path
        working_dir = os.path.dirname(fully_qualified_name)

        # The all dots scenario is special
        if all(char if char == "." else None for char in source):
            importing_source_parts = [""] * len(source)
        else:
            importing_source_parts = source.split(".")

        assert importing_source_parts

        # Process relative path info (if any)
        if not importing_source_parts[0]:
            importing_root = os.path.realpath(working_dir)
            importing_source_parts.pop(0)

            while importing_source_parts and not importing_source_parts[0]:
                potential_importing_root = os.path.dirname(importing_root)

                if potential_importing_root == importing_root:
                    raise InvalidRelativePathError(
                        source_leaf.IterBegin.Line,
                        source_leaf.IterBegin.Column,
                        source,
                        working_dir,
                        source_leaf.IterEnd.Line,
                        source_leaf.IterEnd.Column,
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
            import_type = ImportStatement.ImportType.SourceIsModule
        elif len(import_items) == 1:
            potential_module_name = import_items[0].Name

            source_filename = FindSource(
                os.path.isdir,
                root_suffix=potential_module_name,
            )

            if source_filename is not None:
                import_type = ImportStatement.ImportType.SourceIsDirectory

        if source_filename is None:
            return TranslationUnitsParserObserver.ImportInfo(source, None)

        assert import_type is not None

        # Preserve the value
        object.__setattr__(
            node,
            "Info",
            ImportStatement.NodeInfo(
                {
                    "ImportType": node,
                    "SourceFilename": source_leaf,
                },
                import_type,
                source_filename,
                import_items,
            ),
        )

        return TranslationUnitsParserObserver.ImportInfo(source, source_filename)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _ExtractRawInfo(
        node: Node,
    ) -> Tuple[
        str,                                            # source
        Leaf,                                           # source leaf
        List["ImportStatement.ImportItemInfo"],         # import items
    ]:

        nodes = ExtractSequence(node)
        assert len(nodes) == 5

        # <source>
        source_leaf = cast(Leaf, nodes[1])
        source = cast(str, ExtractToken(source_leaf))

        # Content items
        content_nodes = cast(Node, ExtractOr(cast(Node, nodes[3])))
        assert content_nodes.Type

        if content_nodes.Type.Name == "Grouped":
            content_nodes = cast(Node, ExtractSequence(content_nodes)[2])

        content_nodes = ExtractSequence(content_nodes)
        assert len(content_nodes) == 3

        import_items: List[ImportStatement.ImportItemInfo] = []

        for content_item_node in itertools.chain(
            [content_nodes[0]],
            [
                ExtractSequence(delimited_node)[1]
                for delimited_node in cast(
                    List[Node],
                    ExtractRepeat(cast(Node, content_nodes[1])),
                )
            ],
        ):
            content_item_nodes = ExtractSequence(cast(Node, content_item_node))
            assert len(content_item_nodes) == 2

            content_item_lookup = {}

            key_leaf = cast(Leaf, content_item_nodes[0])
            key = cast(str, ExtractToken(key_leaf))
            content_item_lookup["Name"] = key_leaf

            as_node = ExtractOptional(cast(Optional[Node], content_item_nodes[1]))
            if as_node is not None:
                as_nodes = ExtractSequence(cast(Node, as_node))
                assert len(as_nodes) == 2

                value_leaf = cast(Leaf, as_nodes[1])
                value = cast(str, ExtractToken(value_leaf))
                content_item_lookup["Alias"] = value_leaf
            else:
                value = None

            import_items.append(
                # pylint: disable=too-many-function-args
                ImportStatement.ImportItemInfo(
                    content_item_lookup,
                    key,
                    value,
                ),
            )

        return source, source_leaf, import_items
