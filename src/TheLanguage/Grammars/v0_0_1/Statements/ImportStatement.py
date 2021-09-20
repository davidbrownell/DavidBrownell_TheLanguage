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

from typing import Callable, cast, List, Optional

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
    from ..Common import VisibilityModifier

    from ...GrammarPhrase import CreateParserRegions, ImportGrammarStatement

    from ....Lexer.Phrases.DSL import (
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

    from ....Lexer.TranslationUnitsLexer import (
        Observer as TranslationUnitsLexerObserver,
        UnknownSourceError,
    )

    from ....Parser.ParserInfo import SetParserInfo

    from ....Parser.Statements.ImportStatementParserInfo import (
        ImportItemParserInfo,
        ImportStatementParserInfo,
        ImportType,
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
                    # <visibility>?
                    PhraseItem(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                        arity="?",
                    ),

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
    ) -> TranslationUnitsLexerObserver.ImportInfo:

        assert fully_qualified_name

        # Note that it tempting to try to extract ImportStatementParserInfo here, but we can't do that
        # because the nodes have not yet been fully populated. Extract only what is relevant here, and
        # then extract the full set of data in ExtractParserInfo.
        nodes = ExtractSequence(node)
        assert len(nodes) == 6

        # Source name
        source_leaf = cast(Leaf, nodes[2])
        source_name = cast(str, ExtractToken(source_leaf))

        # Import items
        contents_node = cast(Node, ExtractOr(cast(Node, nodes[4])))

        assert contents_node.Type is not None
        if contents_node.Type.Name == "Grouped":
            contents_node = cast(Node, ExtractSequence(contents_node)[2])

        contents_nodes = ExtractSequence(contents_node)
        assert len(contents_nodes) == 3

        import_items: List[str] = []

        for content_item_node in itertools.chain(
            [contents_nodes[0]],
            [
                ExtractSequence(delimited_node)[1]
                for delimited_node in cast(List[Node], ExtractRepeat(cast(Node, contents_nodes[1])))
            ],
        ):
            content_item_nodes = ExtractSequence(cast(Node, content_item_node))
            assert len(content_item_nodes)

            import_items.append(cast(str, ExtractToken(cast(Leaf, content_item_nodes[0]))))

        # We need to get the source and the items to import, however that information depends on
        # context. The content will fall into one of these scenarios:
        #
        #   A) N import items, source is module name; import items are members of the module
        #   B) 1 import item, source is module name; import item is a member of the module
        #   C) 1 import item, source is a directory; import item is a module name

        # Update the source_roots if we are looking at a relative path
        working_dir = os.path.dirname(fully_qualified_name)

        # The all dots scenario is special
        if all(char if char == "." else None for char in source_name):
            importing_source_parts = [""] * len(source_name)
        else:
            importing_source_parts = source_name.split(".")

        assert importing_source_parts

        # Process relative path info (if any)
        if not importing_source_parts[0]:
            importing_root = os.path.realpath(working_dir)
            importing_source_parts.pop(0)

            while importing_source_parts and not importing_source_parts[0]:
                potential_importing_root = os.path.dirname(importing_root)

                if potential_importing_root == importing_root:
                    assert source_leaf is not None

                    raise InvalidRelativePathError(
                        source_leaf.IterBegin.Line,
                        source_leaf.IterBegin.Column,
                        source_name,
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
            import_type = ImportType.SourceIsModule
        elif len(import_items) == 1:
            potential_module_name = import_items[0]

            source_filename = FindSource(
                os.path.isdir,
                root_suffix=potential_module_name,
            )

            if source_filename is not None:
                import_type = ImportType.SourceIsDirectory

        if source_filename is None:
            return TranslationUnitsLexerObserver.ImportInfo(source_name, None)

        # Cache the import type so that we don't need to calculate it again
        assert import_type is not None

        object.__setattr__(node, "_import_type", import_type)

        return TranslationUnitsLexerObserver.ImportInfo(source_name, source_filename)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ExtractParserInfo(
        node: Node,
    ) -> Optional[ImportGrammarStatement.ExtractParserInfoResult]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 6

        # <visibility>?
        visibility_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], nodes[0])))
        if visibility_node is not None:
            visibility_info = VisibilityModifier.Extract(visibility_node)
        else:
            visibility_info = None

        # <source>
        source_leaf = cast(Leaf, nodes[2])
        source_info = cast(str, ExtractToken(source_leaf))

        # Content items
        contents_node = cast(Node, ExtractOr(cast(Node, nodes[4])))

        assert contents_node.Type is not None
        if contents_node.Type.Name == "Grouped":
            contents_node = cast(Node, ExtractSequence(contents_node)[2])

        contents_nodes = ExtractSequence(contents_node)
        assert len(contents_nodes) == 3

        import_items: List[ImportItemParserInfo] = []

        for content_item_node in itertools.chain(
            [contents_nodes[0]],
            [
                ExtractSequence(delimited_node)[1]
                for delimited_node in cast(List[Node], ExtractRepeat(cast(Node, contents_nodes[1])))
            ],
        ):
            content_item_nodes = ExtractSequence(cast(Node, content_item_node))
            assert len(content_item_nodes) == 2

            key_leaf = cast(Leaf, content_item_nodes[0])
            key_info = cast(str, ExtractToken(key_leaf))

            as_node = cast(Optional[Node], ExtractOptional(cast(Optional[Node], content_item_nodes[1])))
            if as_node is not None:
                as_nodes = ExtractSequence(as_node)
                assert len(as_nodes) == 2

                value_leaf = cast(Leaf, as_nodes[1])
                value_info = cast(str, ExtractToken(value_leaf))
            else:
                value_leaf = None
                value_info = None

            # pylint: disable=too-many-function-args
            import_items.append(
                ImportItemParserInfo(
                    CreateParserRegions(content_item_node, key_leaf, value_leaf),  # type: ignore
                    key_info,
                    value_info,
                ),
            )

        assert import_items

        # Extract the cached import type
        import_type = node._import_type  # type: ignore

        SetParserInfo(
            node,
            ImportStatementParserInfo(
                CreateParserRegions(node, visibility_node, node, source_leaf, contents_node),  # type: ignore
                visibility_info,  # type: ignore
                import_type,
                source_info,
                import_items,
            ),
        )
