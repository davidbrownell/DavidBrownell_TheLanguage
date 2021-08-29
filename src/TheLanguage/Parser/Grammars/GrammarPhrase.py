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
from typing import Any, Callable, List, Optional, Union

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Components.AST import Leaf, Node
    from ..Components.Error import Error

    from ..TranslationUnitsParser import (
        DynamicPhrasesInfo,                             # This is here as a convenience
        Observer as TranslationUnitsParserObserver,
        Phrase,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class ValidationError(Error):
    """Extend the Error baase class to include ending line and column attributes"""

    LineEnd: int
    ColumnEnd: int

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Union[Leaf, Node],
        *args,
    ):
        line_before = node.IterBegin.Line if node.IterBegin is not None else -1
        column_before = node.IterBegin.Column if node.IterBegin is not None else -1

        line_after = node.IterEnd.Line if node.IterEnd is not None else -1
        column_after = node.IterEnd.Column if node.IterEnd is not None else -1

        if isinstance(node, Leaf):
            return cls(
                line_before,
                column_before + (
                    node.Whitespace[1] - node.Whitespace[0] - 1
                    if node.Whitespace else 0
                ),
                line_after,
                column_after,
                *args,
            )

        return cls(
            line_before,
            column_before,
            line_after,
            column_after,
            *args,
        )

    # ----------------------------------------------------------------------
    def __post_init__(self):
        super(ValidationError, self).__post_init__()

        assert self.Line <= self.LineEnd, self
        assert self.Line != self.LineEnd or self.Column <= self.ColumnEnd, self


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
    @dataclass(frozen=True, repr=False)
    class NodeInfo(YamlRepr.ObjectReprImplBase):

        # ----------------------------------------------------------------------
        def __post_init__(
            self,
            **custom_display_funcs: Optional[Callable[[Any], Optional[Any]]],
        ):
            YamlRepr.ObjectReprImplBase.__init__(self, **custom_display_funcs)

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
    @Interface.extensionmethod
    def ValidateNodeSyntax(
        node: Node,
    ) -> Optional[bool]:                    # False to prevent child traversal
        """\
        Opportunity to validate the syntax of a node.

        This method is invoked during calls to Parser.py:Validate and should be invoked after calls
        to Parser.py:Prune.
        """

        # No validation be default
        return None


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
    ) -> TranslationUnitsParserObserver.ImportInfo:
        """\
        Returns ImportInfo for the statement.

        Note that this method is called during the parsing process, so content will not have been
        pruned yet.
        """
        raise Exception("Abstract method")  # pragma: no cover
