# ----------------------------------------------------------------------
# |
# |  ImportStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-19 11:20:45
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the ImportStatement object"""

import itertools
import os
import re

from typing import cast, Callable, List, Generator, Optional, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..GrammarPhrase import AST, ImportGrammarPhrase, TranslationUnitsLexerObserver

    from ..Common import Tokens as CommonTokens
    from ..Common import VisibilityModifier

    from ...Lexer.Phrases.DSL import (
        DynamicPhrasesType,
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

    from ...Parser.Parser import (
        CreateError,
        CreateRegion,
        CreateRegions,
        ErrorException,
    )

    from ...Parser.ParserInfos.Statements.ImportStatementParserInfo import (
        ImportStatementParserInfo,
        ImportStatementItemParserInfo,
        ImportType,
    )


# ----------------------------------------------------------------------
InvalidRelativePathError                    = CreateError(
    "The relative path '{source_name}' is not valid for the origin '{origin_name}'",
    source_name=str,
    origin_name=str,
)


# ----------------------------------------------------------------------
class ImportStatement(ImportGrammarPhrase):
    PHRASE_NAME                             = "Import Statement"

    # ----------------------------------------------------------------------
    def __init__(
        self,
        *file_extensions: str,
    ):
        assert file_extensions

        # Nota that we don't want to be too restrictive here, as we want to be able to import
        # different types of content.
        import_name = RegexToken(
            "<import_name>",
            re.compile(r"(?P<value>[A-Za-z0-9_?\.]+)"),
        )

        # <import_name> ('as' <import_name>)?
        element_phrase_item = PhraseItem(
            name="Element",
            item=[
                # <import_name>
                import_name,

                # ('as' <import_name>)?
                OptionalPhraseItem(
                    name="Suffix",
                    item=[
                        "as",
                        import_name,
                    ],
                ),
            ],
        )

        # <element_phrase_item> (',' <element_phrase_item>)* ','?
        elements_phrase_item = PhraseItem(
            name="Element Items",
            item=[
                # <element_phrase_item>
                element_phrase_item,

                # (',' <element_phrase_item>)*
                ZeroOrMorePhraseItem(
                    name="Comma and Element",
                    item=[
                        ",",
                        element_phrase_item,
                    ],
                ),

                # ','?
                OptionalPhraseItem(
                    name="Trailing Comma",
                    item=",",
                ),
            ],
        )

        super(ImportStatement, self).__init__(
            DynamicPhrasesType.Statements,
            self.PHRASE_NAME,
            [
                # <visibility>?
                OptionalPhraseItem(
                    name="Visibility",
                    item=VisibilityModifier.CreatePhraseItem(),
                ),

                # 'from'
                "from",

                # <source_name>
                import_name,

                # 'import'
                "import",

                # <Content Items>
                PhraseItem(
                    item=(
                        # '(' <elements_phrase_item> ')'
                        PhraseItem(
                            name="Grouped",
                            item=[
                                # '('
                                "(",
                                CommonTokens.PushIgnoreWhitespaceControl,

                                # <elements_phrase_item>
                                elements_phrase_item,

                                # ')'
                                CommonTokens.PopIgnoreWhitespaceControl,
                                ")",
                            ],
                        ),

                        # <elements_phrase_item>
                        elements_phrase_item,
                    ),
                    ambiguities_resolved_by_order=True,
                ),

                CommonTokens.Newline,
            ],
        )

        self.file_extensions                = list(file_extensions)

    # ----------------------------------------------------------------------
    @Interface.override
    def ProcessImportNode(
        self,
        source_roots: List[str],
        fully_qualified_name: str,
        node: AST.Node,
    ) -> TranslationUnitsLexerObserver.ImportInfo:
        # This will be invoked very early in the extraction process, so thinks may not be fully
        # populated. Extract the minimum set of information needed now, and extract the full set
        # of information in ExtractParserInfo.

        nodes = ExtractSequence(node)
        assert len(nodes) == 6

        # <source_name>
        source_leaf = cast(AST.Leaf, nodes[2])
        source_name = ExtractToken(source_leaf)

        # Update the source roots if we are looking at a relative path
        working_dir = os.path.dirname(fully_qualified_name)

        # The all dots scenario is special
        if all(char == "." for char in source_name):
            importing_source_parts = [""] * len(source_name)
        else:
            importing_source_parts = source_name.split(".")

        assert importing_source_parts

        # Process the relative path info (if any)
        if not importing_source_parts[0]:
            importing_root = os.path.realpath(working_dir)
            importing_source_parts.pop(0)

            while importing_source_parts and not importing_source_parts[0]:
                potential_importing_root = os.path.dirname(importing_root)

                if potential_importing_root == importing_root:
                    assert source_leaf is not None

                    raise ErrorException(
                        InvalidRelativePathError.Create(
                            region=CreateRegion(source_leaf),
                            source_name=source_name,
                            origin_name=working_dir,
                        ),
                    )

                importing_root = potential_importing_root
                importing_source_parts.pop(0)

            source_roots = [importing_root, ]

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
            bool,                           # Set to False if more than one item was found (True is not used)
        ] = None

        for import_item_info in self.__class__._EnumImportItemsData(nodes):  # pylint: disable=protected-access
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

                if root_suffix is not None:
                    root = os.path.join(root, root_suffix)

                for file_extension in self.file_extensions:
                    potential_filename = root + file_extension
                    if os.path.isfile(potential_filename):
                        return potential_filename

            return None

        # ----------------------------------------------------------------------

        import_type: Optional[ImportType] = None

        source_filename = FindSource(lambda name: os.path.isdir(os.path.dirname(name)))
        if source_filename is not None:
            import_type = ImportType.source_is_module
        elif isinstance(first_and_only_import_name, str):
            source_filename = FindSource(
                os.path.isdir,
                root_suffix=first_and_only_import_name,
            )

            if source_filename is not None:
                import_type = ImportType.source_is_directory

        if source_filename is None:
            return TranslationUnitsLexerObserver.ImportInfo(source_name, None)

        # Cache info so that we don't need to calculate it all over again
        assert import_type is not None

        object.__setattr__(node, self.__class__._CACHED_IMPORT_INFO_ATTRIBUTE_NAME, import_type)  # pylint: disable=protected-access

        return TranslationUnitsLexerObserver.ImportInfo(source_name, source_filename)

    # ----------------------------------------------------------------------
    @Interface.override
    def GetDynamicContent(
        self,
        node: AST.Node,
    ) -> Optional[ImportGrammarPhrase.GetDynamicContentResult]:
        # TODO: Return attributes and other compiler content made available via this import
        return None

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractParserInfo(
        self,
        node: AST.Node,
    ) -> ImportGrammarPhrase.ExtractParserInfoReturnType:
        import_type = getattr(node, self.__class__._CACHED_IMPORT_INFO_ATTRIBUTE_NAME, None)  # pylint: disable=protected-access
        assert import_type is not None, "Cached import info could not be found; it is likely that this node was rebalanced (which is not expected for nodes associated with import statements)"

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
        source_info = ExtractToken(source_leaf)

        # Imports
        import_items = [
            ImportStatementItemParserInfo.Create(
                CreateRegions(data.node, data.name_leaf, data.alias_leaf),
                data.name_info,
                data.alias_info,
            )
            for data in self.__class__._EnumImportItemsData(nodes)  # pylint: disable=protected-access
        ]

        return ImportStatementParserInfo.Create(
            CreateRegions(node, visibility_node, source_leaf),
            visibility_info,
            source_info,
            import_items,
            import_type,
        )

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    _CACHED_IMPORT_INFO_ATTRIBUTE_NAME      = "_cached_import_info"

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
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _EnumImportItemsData(
        cls,
        nodes: List[Union[None, AST.Leaf, AST.Node]],
    ) -> Generator[
        "ImportStatementItemParserInfoData",
        None,
        None,
    ]:
        assert len(nodes) == 6

        contents_node = cast(AST.Node, ExtractOr(cast(AST.Node, nodes[4])))

        assert contents_node.type is not None
        if contents_node.type.name == "Grouped":
            contents_node = cast(AST.Node, ExtractSequence(contents_node)[2])

        contents_nodes = ExtractSequence(contents_node)
        assert len(contents_nodes) == 3

        for content_item_node in itertools.chain(
            [cast(AST.Node, contents_nodes[0]), ],
            (
                cast(AST.Node, ExtractSequence(delimited_node)[1])
                for delimited_node in cast(List[AST.Node], ExtractRepeat(cast(AST.Node, contents_nodes[1])))
            ),
        ):
            content_item_nodes = ExtractSequence(content_item_node)
            assert len(content_item_nodes) == 2

            # <name>
            name_leaf = cast(AST.Leaf, content_item_nodes[0])
            name_info = ExtractToken(name_leaf)

            # ('as' <alias>)?
            alias_node = cast(Optional[AST.Node], ExtractOptional(cast(Optional[AST.Node], content_item_nodes[1])))
            if alias_node is None:
                alias_info = None
            else:
                alias_nodes = ExtractSequence(alias_node)
                assert len(alias_nodes) == 2

                alias_node = cast(AST.Leaf, alias_nodes[1])
                alias_info = ExtractToken(alias_node)

            yield cls.ImportStatementItemParserInfoData(
                content_item_node,
                name_leaf,
                name_info,
                alias_node,
                alias_info,
            )
