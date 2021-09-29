# ----------------------------------------------------------------------
# |
# |  GrammarInfo.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-29 08:34:55
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Tools and utilities that help creating phrases within a grammar"""

import os

from typing import Any, Callable, cast, Dict, List, Optional, Union

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Lexer.Phrases.DSL import DynamicPhrasesType, Phrase
    from ..Lexer.TranslationUnitsLexer import (
        AST,
        DynamicPhrasesInfo,                             # This is here as a convenience
        Observer as TranslationUnitsLexerObserver,
        Phrase,
    )

    from ..Parser.ParserInfo import Location, Region


# ----------------------------------------------------------------------
class GrammarPhrase(Interface.Interface, YamlRepr.ObjectReprImplBase):
    """An individual phrase within a grammar"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class GetDynamicContentResult(object):
        Attributes: Dict[str, "GrammarPhrase"]
        Expressions: Dict[str, "GrammarPhrase"]

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ExtractParserInfoResult(object):
        # Function that should be called once all the nodes have been validated individually. This
        # can be used by phrases who need context information from their parents to complete
        # validation but can only do so after the parent itself has been validated.
        PostExtractFunc: Optional[Callable[[], None]]   = field(default=None)
        AllowChildTraversal: bool                       = field(default=True)

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type: DynamicPhrasesType,
        phrase: Phrase,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        YamlRepr.ObjectReprImplBase.__init__(
            self,
            Phrase=lambda phrase: phrase.Name,
            **custom_display_funcs,
        )

        self.Type                           = type
        self.Phrase                         = phrase

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def GetDynamicContent(
        node: AST.Node,
    ) -> Optional["GrammarPhrase.GetDynamicContentResult"]:
        """\
        Returns any dynamic content that is made available once an instance of the phrase has been parsed.
        """

        # By default, a phrase does not generate dynamic content
        return None

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ExtractParserInfo(
        node: AST.Node,
    ) -> Optional["GrammarPhrase.ExtractParserInfoResult"]:
        """Extracts parser information from a node"""
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
class ImportGrammarPhrase(GrammarPhrase):
    """Phrase that imports content; this functionality requires special handling during the Lexing process"""

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ProcessImportNode(
        source_roots: List[str],
        fully_qualified_name: str,
        node: AST.Node,
    ) -> TranslationUnitsLexerObserver.ImportInfo:
        """\
        Returns ImportInfo associated with the phrase.

        Note that this method is called during the lexing process, so content will not have been pruned yet.
        """
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
def CreateParserRegion(
    node: Union[AST.Leaf, AST.Node],
) -> Region:
    """Uses information in a node to create a Region"""

    # ----------------------------------------------------------------------
    def CreateLocation(
        iter: Optional[Phrase.NormalizedIterator],
        adjust_for_whitespace=False,
    ) -> Location:
        if iter is None:
            line = -1
            column = -1
        else:
            line = iter.Line
            column = iter.Column

            if (
                isinstance(node, AST.Leaf)
                and adjust_for_whitespace
                and node.Whitespace is not None
            ):
                column += node.Whitespace[1] - node.Whitespace[0] - 1

        return Location(line, column)

    # ----------------------------------------------------------------------

    return Region(
        CreateLocation(
            node.IterBegin,
            adjust_for_whitespace=True,
        ),
        CreateLocation(node.IterEnd),
    )


# ----------------------------------------------------------------------
def CreateParserRegions(
    *nodes: Union[AST.Leaf, AST.Node, Region, None],
) -> List[Optional[Region]]:
    """Creates regions for the provided input"""

    # TODO: Ensure that TheLanguage can handle statements formatted like this
    return [
        None if node is None else
            node if isinstance(node, Region) else
                CreateParserRegion(node)
        for node in nodes
    ]


# ----------------------------------------------------------------------
def GetParentStatementNode(
    node: AST.Node,
) -> Optional[AST.Node]:
    """\
    Returns the statement that is the logical parent of this node.

    This code attempts to handle the complexities of embedded phrases (for example, a statement that
    is made up of other phrases) where this node may be nested multiple levels below what ultimately
    constitutes its parent.
    """

    parent = node.Parent

    while parent is not None:
        if parent.Type is not None and parent.Type.Name.endswith("Statement"):
            break

        parent = parent.Parent

    return cast(Optional[AST.Node], parent)
