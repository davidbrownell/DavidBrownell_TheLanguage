# ----------------------------------------------------------------------
# |
# |  ImportStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-15 14:27:44
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

from typing import Callable, cast, Generator, List, Optional, Tuple, Union

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

    from ...GrammarInfo import AST, DynamicPhrasesType, ImportGrammarPhrase, ParserInfo, TranslationUnitsLexerObserver

    from ....Lexer.Phrases.DSL import (
        CreatePhrase,
        ExtractOptional,
        ExtractOr,
        ExtractRepeat,
        ExtractSequence,
        ExtractToken,
        OptionalPhraseItem,
        PhraseItem,
        RegexToken,
        ZeroOrMorePhraseItem,
    )

    from ....Lexer.TranslationUnitsLexer import (
        UnknownSourceError,
    )

    from ....Parser.Parser import CreateParserRegions

    from ....Parser.Statements.ImportStatementParserInfo import (
        ImportStatementItemParserInfo,
        ImportStatementParserInfo,
        ImportType,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidRelativePathError(UnknownSourceError):
    OriginName: str
    LineEnd: int
    ColumnEnd: int

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The relative path '{SourceName}' is not valid for the origin '{OriginName}'.",
    )


# ----------------------------------------------------------------------
class ImportStatement(ImportGrammarPhrase):
    """\
    Imports content from another file.

    'from' <source_file|source_path> 'import' <content>

    Examples:
        from Module import Foo
        from Module import Bar as _Bar
        from Module2 import Biz, Baz
        from Module.File import A, B, C
        public from Module import X, Y
    """

    PHRASE_NAME                             = "Import Statement"

    # ----------------------------------------------------------------------
    def __init__(
        self,
        *file_extensions: str,
    ):
        assert file_extensions

        # Note that we don't want to be too restrictive here, as we want to be able to import different
        # types of content.
        import_name = RegexToken("<import_name>", re.compile(r"(?P<value>[a-zA-Z0-9\._]+)"))

        # <name> ('as' <name>)?
        content_phrase_item = PhraseItem.Create(
            name="Content Item",
            item=[
                # <name>
                import_name,

                # ('as' <name>)?
                OptionalPhraseItem.Create(
                    name="Suffix",
                    item=[
                        "as",
                        import_name,
                    ],
                ),

            ],
        )

        # <content_phrase_item> (',' <content_phrase_item>)* ','?
        content_phrase_items = PhraseItem.Create(
            name="Content Items",
            item=[
                # <content_phrase_item>
                content_phrase_item,

                # (',' <content_phrase_item>)*
                ZeroOrMorePhraseItem.Create(
                    name="Comma and Content",
                    item=[
                        ",",
                        content_phrase_item,
                    ],
                ),

                # ','?
                OptionalPhraseItem.Create(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        )

        super(ImportStatement, self).__init__(
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    # <visibility>?
                    OptionalPhraseItem.Create(
                        name="Visibility",
                        item=VisibilityModifier.CreatePhraseItem(),
                    ),

                    # 'from'
                    "from",

                    # <name>
                    import_name,

                    # 'import'
                    "import",

                    # Content Items
                    PhraseItem.Create(
                        item=(
                            # '(' <content_phrase_items> ')'
                            PhraseItem.Create(
                                name="Grouped",
                                item=[
                                    # '('
                                    "(",
                                    CommonTokens.PushIgnoreWhitespaceControl,

                                    # <content_phrase_items>
                                    content_phrase_items,

                                    # ')'
                                    CommonTokens.PopIgnoreWhitespaceControl,
                                    ")",
                                ],
                            ),

                            # <content_phrase_items>
                            content_phrase_items
                        ),

                        # Use the order to disambiguate between group clauses and tuples.
                        ambiguities_resolved_by_order=True,
                    ),

                    CommonTokens.Newline,
                ],
            ),
        )

        self.FileExtensions                 = list(file_extensions)

    # ----------------------------------------------------------------------
    @Interface.override
    def ProcessImportNode(
        self,
        source_roots: List[str],
        fully_qualified_name: str,
        node: AST.Node,
    ) -> TranslationUnitsLexerObserver.ImportInfo:
        assert fully_qualified_name

        # Note that it tempting to try to extract ImportStatementParserInfo here, but we can't do that
        # because the nodes have not yet been fully populated. Extract only what is relevant here, and
        # then extract the full set of data in ExtractParserInfo.
        nodes = ExtractSequence(node)
        assert len(nodes) == 6

        # Source name
        source_leaf = cast(AST.Leaf, nodes[2])
        source_name = cast(str, ExtractToken(source_leaf))

        # Update the source_roots if we are looking at a relative path
        working_dir = os.path.dirname(fully_qualified_name)

        # The all dots scenario is special
        if all(char == "." for char in source_name):
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

            source_roots = [importing_root, ]

        # Import items
        contents_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[4])))

        assert contents_node.Type is not None
        if contents_node.Type.Name == "Grouped":
            contents_node = cast(AST.Node, ExtractSequence(contents_node)[2])

        contents_nodes = ExtractSequence(contents_node)
        assert len(contents_nodes) == 3

        # We need to get the source and the items to import, however that information depends on
        # context. The content will fall into one of these scenarios:
        #
        #   A) N import items, source is module name; import items are members of the module
        #   B) 1 import item, source is module name; import item is a member of the module
        #   C) 1 import item, source is a directory; import item is a module name
        #
        # Figure out which scenario we are looking at

        first_and_only_import_name: Union[
            None,                           # No items have been found yet
            str,                            # The name of the first item
            bool,                           # Set to False if more than one item was found
        ] = None

        for import_item_info in self._EnumImportItemsData(nodes):
            if first_and_only_import_name is None:
                first_and_only_import_name = import_item_info.name_info
            else:
                first_and_only_import_name = False
                break

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
        elif isinstance(first_and_only_import_name, str):
            source_filename = FindSource(
                os.path.isdir,
                root_suffix=first_and_only_import_name,
            )

            if source_filename is not None:
                import_type = ImportType.SourceIsDirectory

        if source_filename is None:
            return TranslationUnitsLexerObserver.ImportInfo(source_name, None)

        # Cache info so that we don't need to calculate it again
        assert import_type is not None

        object.__setattr__(node, "_cached_import_info", import_type)

        return TranslationUnitsLexerObserver.ImportInfo(source_name, source_filename)

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def GetDynamicContent(
        node: AST.Node,
    ) -> Optional[ImportGrammarPhrase.GetDynamicContentResult]:
        # TODO: Return attributes and other compiler content made available via this import
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractParserInfo(
        self,
        node: AST.Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
        Tuple[ParserInfo, Callable[[], ParserInfo]],
    ]:
        import_type = getattr(node, "_cached_import_info", None)
        assert import_type is not None, "Cached import info could not be found; it is likely that this node was rebalanced as part of a left-recursive phrase"

        nodes = ExtractSequence(node)
        assert len(nodes) == 6

        # <visibility>?
        visibility_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], nodes[0])))
        if visibility_node is None:
            visibility_info = None
        else:
            visibility_info = VisibilityModifier.Extract(visibility_node)

        # <source>
        source_leaf = cast(AST.Leaf, nodes[2])
        source_info = cast(str, ExtractToken(source_leaf))

        # Imports
        import_items = [
            # pylint: disable=too-many-function-args
            ImportStatementItemParserInfo(
                CreateParserRegions(data.node, data.name_leaf, data.alias_leaf),  # type: ignore
                data.name_info,
                data.alias_info,
            )
            for data in self._EnumImportItemsData(nodes)
        ]

        return ImportStatementParserInfo(
            CreateParserRegions(node, visibility_node, source_leaf),  # type: ignore
            visibility_info,  # type: ignore
            source_info,
            import_items,
            import_type,
        )

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass
    class ImportStatementItemParserInfoData(object):
        node: AST.Node

        name_leaf: AST.Leaf
        name_info: str

        alias_leaf: Optional[AST.Leaf]
        alias_info: Optional[str]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert (
                (self.alias_leaf is None and self.alias_info is None)
                or (self.alias_leaf is not None and self.alias_info is not None)
            )

    # ----------------------------------------------------------------------
    # |
    # |  Private Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def _EnumImportItemsData(
        cls,
        nodes: List[Union[None, AST.Leaf, AST.Node]],
    ) -> Generator[
        # Note that we can't use ImportStatementItemParserInfo here, as it will validate regions when constructed
        # and regions may not be valid yes since this will be invoked so early within the lexing process.
        "ImportStatementItemParserInfoData",
        None,
        None,
    ]:
        assert len(nodes) == 6

        contents_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[4])))

        assert contents_node.Type is not None
        if contents_node.Type.Name == "Grouped":
            contents_node = cast(AST.Node, ExtractSequence(contents_node)[2])

        contents_nodes = ExtractSequence(contents_node)
        assert len(contents_nodes) == 3

        for content_item_node in itertools.chain(
            [contents_nodes[0]],
            [
                ExtractSequence(delimited_node)[1]
                for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, contents_nodes[1])))
            ],
        ):
            content_item_nodes = ExtractSequence(cast(AST.Node, content_item_node))
            assert len(content_item_nodes) == 2

            # <name>
            name_leaf = cast(AST.Leaf, content_item_nodes[0])
            name_info = cast(str, ExtractToken(name_leaf))

            # ('as' <name>)?
            alias_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], content_item_nodes[1])))
            if alias_node is None:
                alias_info = None
            else:
                alias_node = cast(AST.Leaf, ExtractSequence(alias_node)[1])
                alias_info = cast(str, ExtractToken(alias_node))

            yield cls.ImportStatementItemParserInfoData(
                cast(AST.Node, content_item_node),
                name_leaf,
                name_info,
                alias_node,
                alias_info,
            )
