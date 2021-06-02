# ----------------------------------------------------------------------
# |
# |  ImportStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-05-23 16:34:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains statements that import code"""

import os
import re

from collections import OrderedDict
from typing import cast, List, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from . import Tokens

    from ..GrammarStatement import ImportGrammarStatement

    from ...ParserImpl.MultifileParser import (
        Leaf,
        Node,
        Observer as MultifileParserObserver,
        UnknownSourceError,
    )

    from ...ParserImpl.Statement import Statement

    from ...ParserImpl.Token import (
        PopIgnoreWhitespaceControlToken,
        PushIgnoreWhitespaceControlToken,
        RegexToken,
        Token,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidRelativePathError(UnknownSourceError):
    OriginName: str

    MessageTemplate                         = Interface.DerivedProperty("The relative path '{SourceName}' is not valid with the origin '{OriginName}'")


# ----------------------------------------------------------------------
_import_name_token                          = RegexToken("<name>", re.compile(r"(?P<value>[a-zA-Z0-9_]+)"))


_import_content_item_statement              = [
    # <import_name> as <new_import_name>
    Statement(
        "Renamed",
        _import_name_token,
        RegexToken("'as'", re.compile("as")),
        _import_name_token,
    ),

    # <import_name>
    _import_name_token,
]


# <content_item_statement> (',' <content_item_statement>)+ ','?
_import_content_items_statement             = Statement(
    "Items",
    _import_content_item_statement,
    (
        Statement(
            "Comma and Statement",
            Tokens.CommaToken,
            _import_content_item_statement,
        ),
        0,
        None,
    ),
    (
        Statement(
            "Comma",
            Tokens.CommaToken,
        ),
        0,
        1,
    ),
)


del _import_content_item_statement
del _import_name_token


# ----------------------------------------------------------------------
class ImportStatement(ImportGrammarStatement):
    """'from' <source> 'import' <content>"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        *file_extensions: str,
    ):
        assert file_extensions

        super(ImportStatement, self).__init__(
            Statement(
                "Import",
                RegexToken("'from'", re.compile("from")),
                RegexToken("<source>", re.compile(r"(?P<value>[a-zA-Z\.][a-zA-Z0-9\._]*)")),
                RegexToken("'import'", re.compile("import")),
                [
                    # '(' <content_items_statement> ')'
                    Statement(
                        "Grouped Items",
                        Tokens.LParenToken,
                        PushIgnoreWhitespaceControlToken(),
                        _import_content_items_statement,
                        PopIgnoreWhitespaceControlToken(),
                        Tokens.RParenToken,
                    ),
                    _import_content_items_statement,
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
    ) -> MultifileParserObserver.ImportInfo:

        # Calculate the source
        original_source = node.Children[1].Value.Match.group("value")

        # The logic with all dots is slightly different from the standard logic
        if all(c if c == "." else None for c in original_source):
            original_source_parts = [""] * len(original_source)
        else:
            original_source_parts = original_source.split(".")

        if not original_source_parts[0]:
            # If here, original_source started with a '.'
            source_root = os.path.realpath(os.path.dirname(fully_qualified_name))
            original_source_parts.pop(0)

            while original_source_parts and not original_source_parts[0]:
                potential_source_root = os.path.dirname(source_root)
                if potential_source_root == source_root:
                    raise InvalidRelativePathError(
                        node.Children[1].Iter.Line,
                        node.Children[1].Iter.Column,
                        original_source,
                        os.path.dirname(fully_qualified_name),
                    )

                source_root = potential_source_root
                original_source_parts.pop(0)

            source_roots = [source_root]

        # Calculate the items to import
        import_result = node.Children[3]

        assert len(import_result.Children) == 1
        import_result = import_result.Children[0]

        if import_result.Type == _import_content_items_statement:
            import_items = self._ProcessContentItems(import_result)

        elif import_result.Type.Name == "Grouped Items":
            for child in import_result.Children:
                if child.Type == _import_content_items_statement:
                    import_items = self._ProcessContentItems(child)
                    break

        else:
            assert False, import_result  # pragma: no cover

        # At this point, we don't know if the source points to a directory or
        # a filename. We are in one of these scenarios:
        #
        #   A) N import items, source is a filename, import items are objects
        #   B) 1 import item, source is a filename, import item is object
        #   C) 1 import item, source is a directory, import item is a filename

        # ----------------------------------------------------------------------
        def FindSource(
            is_valid_func,
            root_suffix=None,
        ):
            for source_root in source_roots:
                root = os.path.join(source_root, *original_source_parts)
                if not is_valid_func(root):
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
            source_filename = FindSource(
                os.path.isdir,
                root_suffix=next(iter(import_items.keys())),
            )

        if source_filename is not None:
            node.source_filename = source_filename
            node.import_items = import_items

        return MultifileParserObserver.ImportInfo(original_source, source_filename)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @classmethod
    def _ProcessContentItems(
        cls,
        node: Node,
    ):
        # Get the nodes (and ignore the leaves)
        nodes = []

        for child in node.Children:
            if isinstance(child, Node):
                nodes.append(child)

        assert len(nodes) == 3, nodes

        # Extract the import items from the ndoes
        import_items = OrderedDict()

        key, value = cls._ProcessContentItem(nodes[0])
        import_items[key] = value

        for child in nodes[1].Children:
            for child_node in child.Children:
                if isinstance(child_node, Node):
                    key, value = cls._ProcessContentItem(child_node)
                    import_items[key] = value

                    break

        return import_items

    # ----------------------------------------------------------------------
    @staticmethod
    def _ProcessContentItem(
        node: Node,
    ) -> Tuple[str, str]:
        assert len(node.Children) == 1, node
        node = node.Children[0]

        if isinstance(node.Type, Statement):
            assert len(node.Children) == 3, node

            return (
                cast(Leaf, node.Children[0]).Value.Match.group("value"),
                cast(Leaf, node.Children[2]).Value.Match.group("value"),
            )

        elif isinstance(node.Type, Token):
            result = cast(Leaf, node).Value.Match.group("value")

            return result, result

        else:
            assert False, node.Type  # pragma: no cover

        # We will never get here, but need to make the linter happy
        return "", ""  # pragma: no cover
