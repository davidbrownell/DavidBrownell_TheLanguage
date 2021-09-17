# ----------------------------------------------------------------------
# |
# |  GrammarPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-10 14:48:11
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

from enum import auto, Enum
from typing import cast, Any, Callable, Dict, List, Optional, Union

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
    from ..Parser.ParserInfo import (
        Location as ParserLocation,
        Region as ParserRegion,
    )

    from ..Lexer.Components.AST import Leaf, Node

    from ..Lexer.TranslationUnitsLexer import (
        DynamicPhrasesInfo,                             # This is here as a convenience
        Observer as TranslationUnitsLexerObserver,
        Phrase,
    )


# ----------------------------------------------------------------------
class GrammarPhrase(Interface.Interface, YamlRepr.ObjectReprImplBase):
    """An individual phrase within a grammar"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class Type(Enum):
        Expression                          = auto()
        Name                                = auto()
        Statement                           = auto()
        Type                                = auto()

    # ----------------------------------------------------------------------
    # TODO: This will go away in favor of ParserInfo
    @dataclass(frozen=True, repr=False)
    class NodeInfo(YamlRepr.ObjectReprImplBase):
        TokenLookup: Dict[str, Union[Leaf, Node, None]]

        # ----------------------------------------------------------------------
        def __post_init__(
            self,
            **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
        ):
            YamlRepr.ObjectReprImplBase.__init__(
                self,
                TokenLookup=None,
                **custom_display_funcs,
            )

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
        type_value: "GrammarPhrase.Type",
        phrase: Phrase,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        YamlRepr.ObjectReprImplBase.__init__(
            self,
            Phrase=lambda phrase: phrase.Name,
            **custom_display_funcs,
        )

        self.TypeValue                      = type_value
        self.Phrase                         = phrase

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ExtractParserInfo(
        node: Node,
    ) -> Optional["GrammarPhrase.ExtractParserInfoResult"]:
        """\
        Opportunity to validate the syntax of a node.

        This method is invoked during calls to Lexer.py:Validate and should be invoked after calls
        to Lexer.py:Prune.
        """
        raise Exception("Abstract method")


# ----------------------------------------------------------------------
class ImportGrammarStatement(GrammarPhrase):
    """Grammar statement that imports content; this functionality requires special handling during the parsing process"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        statement: Phrase,
        **custom_display_funcs: Callable[[Any], Optional[str]],
    ):
        super(ImportGrammarStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            statement,
            **custom_display_funcs,
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def ProcessImportStatement(
        source_roots: List[str],
        fully_qualified_name: str,
        node: Node,
    ) -> TranslationUnitsLexerObserver.ImportInfo:
        """\
        Returns ImportInfo for the statement.

        Note that this method is called during the parsing process, so content will not have been
        pruned yet.
        """
        raise Exception("Abstract method")  # pragma: no cover


# ----------------------------------------------------------------------
def CreateParserRegion(
    node: Union[Leaf, Node],
) -> ParserRegion:
    # ----------------------------------------------------------------------
    def CreateLocation(
        iter: Optional[Phrase.NormalizedIterator],
        adjust_for_whitespace=False,
    ) -> ParserLocation:
        if iter is None:
            line = -1
            column = -1
        else:
            line = iter.Line
            column = iter.Column

            if (
                isinstance(node, Leaf)
                and adjust_for_whitespace
                and node.Whitespace is not None
            ):
                column += node.Whitespace[1] - node.Whitespace[0] - 1

        # pylint: disable=too-many-function-args
        return ParserLocation(line, column)

    # ----------------------------------------------------------------------

    # pylint: disable=too-many-function-args
    return ParserRegion(
        CreateLocation(
            node.IterBegin,
            adjust_for_whitespace=True,
        ),
        CreateLocation(node.IterEnd),
    )


# ----------------------------------------------------------------------
def CreateParserRegions(
    *nodes: Union[Leaf, ParserRegion, Node, None],
) -> List[Optional[ParserRegion]]:
    return [
        None if node is None else
            node if isinstance(node, ParserRegion) else
                CreateParserRegion(node)
        for node in nodes
    ]


# ----------------------------------------------------------------------
def GetParentNode(
    node: Node,
) -> Optional[Node]:
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

    return cast(Optional[Node], parent)
