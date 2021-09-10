# ----------------------------------------------------------------------
# |
# |  MultilineStatementBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-03 10:51:57
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the MultilineStatementBase object"""

import os
import re

from typing import cast, Optional

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ...Common import Tokens as CommonTokens
    from ....GrammarPhrase import GrammarPhrase, ValidationError

    from .....Parser.Components.Normalize import TripletContentRegexTemplate
    from .....Parser.Components.Token import RegexToken
    from .....Parser.Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMultilineHeaderError(ValidationError):
    Header: str

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The header ('{Header}') must be followed by a new line.",
    )

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Leaf,
        header: str,
    ):
        return cls(
            node.IterBegin.Line,
            node.IterBegin.Column,
            node.IterBegin.Line,
            node.IterBegin.Column + len(header),
            header,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMultilineFooterError(ValidationError):
    Header: str
    Footer: str
    LineOffset: int

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The footer ('{Footer}') must be aligned vertically with the header ('{Header}') [Line {LineOffset}]."
    )

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Leaf,
        header: str,
        footer: str,
        line_offset: int,
    ):
        return cls(
            node.IterEnd.Line,
            node.IterEnd.Column - len(footer),
            node.IterEnd.Line,
            node.IterEnd.Column,
            header,
            footer,
            line_offset,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMultilineIndentError(ValidationError):
    Header: str
    LineOffset: int

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Multi-line content must be aligned vertically with the header ('{Header}') [Line {LineOffset}].",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMultilineContentError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Multi-line content cannot be empty.")  # type: ignore


# ----------------------------------------------------------------------
class MultilineStatementBase(GrammarPhrase):
    """\
    Base class for statements delimited by a header and footer that span multiple lines.

    Examples:
        <<<
        This is a docstring.
        >>>

        <<<!!!
        This is compiler data.

        !!!>>>
    """

    # ----------------------------------------------------------------------
    def __init__(
        self,
        phrase_name: str,
        header: str,
        footer: str,
    ):
        super(MultilineStatementBase, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=phrase_name,
                item=[
                    RegexToken(
                        "Multi-line Content",
                        re.compile(
                            TripletContentRegexTemplate.format(
                                header=re.escape(header),
                                footer=re.escape(footer),
                            ),
                            re.DOTALL | re.MULTILINE,
                        ),
                        is_multiline=True,
                    ),

                    CommonTokens.Newline,
                ],
            ),
        )

        self.Header                         = header
        self.Footer                         = footer

    # ----------------------------------------------------------------------
    @Interface.override
    def ValidateSyntax(
        self,
        node: Node,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        # TODO: Revisit this

        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        leaf = cast(Leaf, nodes[0])
        value = cast(str, ExtractToken(leaf))

        if not value.startswith("\n"):
            raise InvalidMultilineHeaderError.FromNode(leaf, self.Header)
        value = value[1:]

        lines = value.split("\n")

        expected_indentation_len = leaf.IterBegin.Offset - leaf.IterBegin.LineInfo.OffsetStart

        if expected_indentation_len:
            expected_indentation = leaf.IterBegin.Content[leaf.IterBegin.Offset - expected_indentation_len : leaf.IterBegin.Offset]

            for line_index, line in enumerate(lines):
                if not line.startswith(expected_indentation):
                    raise InvalidMultilineIndentError.FromNode(leaf, self.Header, line_index + 1)

                lines[line_index] = line[expected_indentation_len:]

        # The last line should be empty, as it should be the prefix and footer
        if lines[-1]:
            raise InvalidMultilineFooterError.FromNode(leaf, self.Header, self.Footer, len(lines))

        lines.pop()

        value = "\n".join(lines)
        if not value:
            raise InvalidMultilineContentError.FromNode(leaf)

        return self._ValidateSyntaxImpl(node, leaf, value)

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @Interface.abstractmethod
    def _ValidateSyntaxImpl(
        self,
        node: Node,
        leaf: Leaf,
        value: str,
    ) -> Optional[GrammarPhrase.ValidateSyntaxResult]:
        raise Exception("Abstract method")  # pragma: no cover
