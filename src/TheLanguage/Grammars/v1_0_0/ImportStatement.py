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
    from . import CommonStatements
    from . import CommonTokens

    from ..GrammarStatement import ImportGrammarStatement

    from ...ParserImpl.Error import Error

    from ...ParserImpl.MultifileParser import (
        Leaf,
        Node,
        Observer as MultifileParserObserver,
        UnknownSourceError
    )

    from ...ParserImpl.Statement import Statement
    from ...ParserImpl.Token import RegexToken


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidRelativePathError(UnknownSourceError):
    OriginName: str
    LineEnd: int
    ColumnEnd: int

    MessageTemplate                         = Interface.DerivedProperty("The relative path '{SourceName}' is not valid for the origin '{OriginName}'")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidModuleNameError(Error):
    ModuleName: str

    MessageTemplate                         = Interface.DerivedProperty("'{ModuleName}' is not valid module name")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidModuleExportNameError(Error):
    ExportName: str

    MessageTemplate                         = Interface.DerivedProperty("'{ExportName}' is not a valid module export name")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidModuleExportPrivateNameError(Error):
    ExportName: str

    MessageTemplate                         = Interface.DerivedProperty("'{ExportName}' is private and may not be imported")


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

        # Calculate the source
        original_source = node.Children[1].Value.Match.group("value")

        # The logic with all dots is slightly different from the standard logic
        if all(c if c == "." else None for c in original_source):
            original_source_parts = [""] * len(original_source)
        else:
            original_source_parts = original_source.split(".")

        if not original_source_parts[0]:
            # If here, the source started with a dot and we are looking at a path relative to
            # the fully qualified name
            source_root = os.path.realpath(os.path.dirname(fully_qualified_name))
            original_source_parts.pop(0)

            while original_source_parts and not original_source_parts[0]:
                potential_source_root = os.path.dirname(source_root)
                if potential_source_root == source_root:
                    raise InvalidRelativePathError(
                        node.Children[1].IterBefore.Line,
                        node.Children[1].IterBefore.Column,
                        original_source,
                        os.path.dirname(fully_qualified_name),
                        node.Children[1].IterAfter.Line,
                        node.Children[1].IterAfter.Column,
                    )

                source_root = potential_source_root
                original_source_parts.pop(0)

            source_roots = [source_root]

        # Calculate the items to import
        import_result = node.Children[3]

        assert len(import_result.Children) == 1
        import_result = import_result.Children[0]

        if import_result.Type == self._content_items_statement:
            import_items = self._ProcessContentItems(import_result)

        elif import_result.Type.Name == "Grouped Items":
            for child in import_result.Children:
                if child.Type == self._content_items_statement:
                    import_items = self._ProcessContentItems(child)
                    break

        else:
            assert False, import_result  # pragma: no cover

        # At this point, we don't know if the source points to a directory or
        # a filename. We are in one of these scenarios:
        #
        #   A) N import items, source is filename; import items are members of the module
        #   B) 1 import item, source is filename; import item is a member of the module
        #   C) 1 import item, source is a directory; import item is a filename

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
            source_filename = FindSource(
                os.path.isdir,
                root_suffix=next(iter(import_items.keys())),
            )

        if source_filename is None:
            return MultifileParserObserver.ImportInfo(original_source, None)

        # Validate the source filename
        module_name = os.path.splitext(os.path.basename(source_filename))[0]

        if CommonStatements.MatchRegexStatement(
            module_name,
            CommonStatements.ModuleNameStatement,
        ) == CommonStatements.MatchRegexStatementResult.NoMatch:
            pass # BugBug raise InvalidModuleNameError(
            pass # BugBug     1, 1, # BugBug
            pass # BugBug     module_name,
            pass # BugBug )

        # Validate the import items if we aren't in scenario C
        if len(import_items) != 1 or module_name not in import_items:
            for k, v in import_items.items():
                validate_items = [k]

                if v != k:
                    validate_items.append(v)

                results = []

                for validate_item in validate_items:
                    result = CommonStatements.MatchRegexStatement(
                        validate_item,
                        CommonStatements.ClassNameStatement,
                        CommonStatements.FunctionNameStatement,
                        CommonStatements.VariableNameStatement,
                    )

                    if result == CommonStatements.MatchRegexStatementResult.NoMatch:
                        pass # BugBug raise InvalidModuleExportNameError(
                        pass # BugBug     1, 1, # BugBug
                        pass # BugBug     validate_item,
                        pass # BugBug )

                    results.append(result)

                # We should never attempt to import a private member
                if results[0] == CommonStatements.MatchRegexStatementResult.Private:
                    raise InvalidModuleExportPrivateNameError(
                        1, 1, # BugBug
                        validate_items[0],
                    )

                # BugBug: We should never attempt to import a protected member
                # outside of the current directory


        # Cache these values for later so we don't need to reparse the content
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
    ) -> Dict[str, str]:
        # Get the nodes (and ignore the leaves)
        nodes = [child for child in node.Children if isinstance(child, Node)]
        assert len(nodes) == 3, nodes

        # Extract the import items
        import_items = OrderedDict()

        key, value = cls._ProcessContentItem(nodes[0])
        import_items[key] = value

        for child in nodes[1].Children:
            for child_node in child.Children:
                if not isinstance(child_node, Node):
                    continue

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
            leaves = [cast(Leaf, child) for child in node.Children if isinstance(child, Leaf) and not child.IsIgnored]
            assert len(leaves) == 3, leaves

            return (
                leaves[0].Value.Match.group("value"),
                leaves[2].Value.Match.group("value"),
            )

        elif isinstance(node.Type, RegexToken):
            result = cast(Leaf, node).Value.Match.group("value")

            return result, result

        else:
            assert False, node.Type  # pragma: no cover

        # We will never get here, but need to make the linter happy
        return "", ""  # pragma: no cover
