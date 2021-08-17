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

from collections import OrderedDict
from enum import auto, Enum
from typing import Callable, cast, Dict, List, Optional, Tuple, Union

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

    from ....Phrases.DSL import (
        CreatePhrase,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
        RegexToken,
    )

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
    @dataclass(frozen=True)
    class NodeInfo(CommonEnvironment.ObjectReprImplBase):
        ImportType: "ImportStatement.ImportType"
        SourceFilename: str
        ImportItems: Dict[str, str]
        ImportItemsLookup: Dict[int, Leaf]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.SourceFilename
            assert self.ImportItems
            assert self.ImportItems

            CommonEnvironment.ObjectReprImplBase.__init__(
                self,
                ImportItemsLookup=None,
            )

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

        # (<name> 'as' <name>) | <name>
        content_item = PhraseItem(
            name="Content Item",
            item=(
                # <name> 'as' <name>
                [
                    CommonTokens.GenericName,
                    "as",
                    CommonTokens.GenericName,
                ],

                # <name>
                CommonTokens.GenericName,
            ),
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
                    (
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

        # The all dots scenario is special
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
            import_type = ImportStatement.ImportType.SourceIsModule
        elif len(raw_items) == 1:
            potential_module_name = next(iter(raw_items.keys()))

            source_filename = FindSource(
                os.path.isdir,
                root_suffix=potential_module_name,
            )

            if source_filename is not None:
                import_type = ImportStatement.ImportType.SourceIsDirectory

        if source_filename is None:
            return TranslationUnitsParserObserver.ImportInfo(raw_source, None)

        assert import_type is not None

        # Preserve the value
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
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _ExtractRawInfo(
        node: Node,
    ) -> Tuple[str, Dict[str, str], Dict[int, Leaf]]:

        nodes = ExtractSequence(node)
        assert len(nodes) == 5

        leaf_lookup: Dict[int, Leaf] = {}

        # <source>
        source_leaf = cast(Leaf, nodes[1])
        source = cast(str, ExtractToken(source_leaf))

        leaf_lookup[id(source)] = source_leaf

        # Content items
        items: Dict[str, str] = OrderedDict()

        content_items = ExtractOr(cast(Node, nodes[3]))
        assert content_items.Type

        if content_items.Type.Name == "Grouped":
            content_items = ExtractSequence(cast(Node, content_items))
            assert len(content_items) == 5

            content_items = content_items[2]

        content_items = ExtractSequence(cast(Node, content_items))
        assert len(content_items) == 3

        for content_item in itertools.chain(
            [content_items[0]],
            [ExtractSequence(node)[1] for node in cast(List[Node], ExtractRepeat(cast(Node, content_items[1])))],
        ):
            content_item = ExtractOr(cast(Node, content_item))

            if isinstance(content_item, Leaf):
                key_leaf = content_item
                key = ExtractToken(key_leaf)

                value_leaf = key_leaf
                value = key

            elif isinstance(content_item, Node):
                as_items = ExtractSequence(content_item)
                assert len(as_items) == 3

                key_leaf = cast(Leaf, as_items[0])
                key = ExtractToken(key_leaf)

                value_leaf = cast(Leaf, as_items[2])
                value = ExtractToken(value_leaf)

            else:
                assert False, content_item  # pragma: no cover

            assert key
            assert value

            items[key] = value
            leaf_lookup[id(key)] = key_leaf
            leaf_lookup[id(value)] = value_leaf

        return source, items, leaf_lookup
