# ----------------------------------------------------------------------
# |
# |  GrammarPhrase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-04 09:22:12
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the GrammarPhrase object"""

import os

from typing import Any, Callable, cast, Dict, List, Optional

import inflect as inflect_mod

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Lexer.Components import AST

    from ..Lexer.Phrases.DSL import (       # pylint: disable=unused-import
        DefaultCommentToken,
        DynamicPhrasesType,
        Phrase,
        RegexToken,                         # Imported as a convenience
    )

    from ..Lexer.TranslationUnitsLexer import (
        Observer as TranslationUnitsLexerObserver,
    )

    from ..Parser.Diagnostics import DiagnosticsError
    from ..Parser.Parser import ParseObserver


# ----------------------------------------------------------------------
inflect                                     = inflect_mod.engine()


# ----------------------------------------------------------------------
CommentToken                                = DefaultCommentToken


# ----------------------------------------------------------------------
class GrammarPhrase(Interface.Interface, ObjectReprImplBase):
    """An individual phrase within a grammar"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class GetDynamicContentResult(object):
        attributes: Dict[str, "GrammarPhrase"]
        expressions: Dict[str, "GrammarPhrase"]

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        type_param: DynamicPhrasesType,
        phrase: Phrase,
        **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
    ):
        # Verify that the phrase name has the expected suffix
        singular_suffix = inflect.singular_noun(type_param.name)
        assert isinstance(singular_suffix, str), type_param.name
        assert phrase.name.endswith(" {}".format(singular_suffix)), (phrase.name, singular_suffix)

        ObjectReprImplBase.__init__(
            self,
            phrase=lambda value: value.name,
            **custom_display_funcs,
        )

        self.type                           = type_param
        self.phrase                         = phrase

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.extensionmethod
    def GetDynamicContent(
        node: AST.Node,  # pylint: disable=unused-argument
    ) -> Optional["GrammarPhrase.GetDynamicContentResult"]:
        """Returns any dynamic content that is made available once an instance of the phrase has been lexed"""

        # By default, a phrase does not generate dynamic content
        return None

    # ----------------------------------------------------------------------
    ExtractParserPhraseReturnType           = ParseObserver.ExtractParserPhraseReturnType

    def ExtractParserPhrase(
        self,
        node: AST.Node,
    ) -> "GrammarPhrase.ExtractParserPhraseReturnType":
        try:
            return self._ExtractParserPhraseImpl(node)
        except DiagnosticsError as ex:
            return ex

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _ExtractParserPhraseImpl(
        node: AST.Node,
    ) -> "GrammarPhrase.ExtractParserPhraseReturnType":
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
def GetParentStatementNode(
    node: AST.Node,
) -> Optional[AST.Node]:
    """\
    Returns the statement that is the logical parent of this node.

    This code attempts to handle the complexities of embedded phrases (for example, a statement that
    is made up of other phrases) where this node may be nested multiple levels below what ultimately
    constitutes its parent.
    """

    parent = node

    while parent is not None:
        if parent.type is not None and parent.type.name.endswith("Statement"):
            break

        parent = parent.parent

    return cast(AST.Node, parent)
