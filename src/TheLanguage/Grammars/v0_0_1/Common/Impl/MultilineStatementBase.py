# ----------------------------------------------------------------------
# |
# |  MultilineStatementBase.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-08 14:15:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains functionality useful when creating statements that span multiple lines"""

import os
import re

from typing import Callable, cast, Optional, Tuple, Union

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

    from ....Error import Error
    from ....GrammarInfo import GrammarPhrase

    from .....Lexer.Components.Normalize import MultilineTokenDelimiterRegexTemplate
    from .....Lexer.Components.Token import RegexToken
    from .....Lexer.Phrases.DSL import (
        CreatePhrase,
        DynamicPhrasesType,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
    )

    from .....Parser.ParserInfo import Location, ParserInfo, Region


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMultilineHeaderError(Error):
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
            Region(
                Location(node.IterBegin.Line, node.IterBegin.Column),
                Location(node.IterBegin.Line, node.IterBegin.Column + len(header)),
            ),
            header,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMultilineFooterError(Error):
    Header: str
    Footer: str
    LineOffset: int

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "The footer ('{Footer}') must be aligned horizontally with the header ('{Header}') [Line {LineOffset}].",
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
            Region(
                Location(node.IterEnd.Line, node.IterEnd.Column - len(footer)),
                Location(node.IterEnd.Line, node.IterEnd.Column),
            ),
            header,
            footer,
            line_offset,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMultilineIndentError(Error):
    Header: str
    LineOffset: int

    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Multi-line content must be aligned horizontally with the header ('{Header}') [Line {LineOffset}].",
    )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidMultilineContentError(Error):
    MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
        "Multi-line content cannot be empty.",
    )


# ----------------------------------------------------------------------
class MultilineStatementBase(GrammarPhrase):
    """\
    Base class for statements delimited by a header and footer that span multiple lines.

    Examples:
        <<<
        A docstring
        >>>

        <<<!!!
        Compiler content
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
            DynamicPhrasesType.Statements,
            CreatePhrase(
                name=phrase_name,
                item=[
                    RegexToken(
                        "Multi-line Content",
                        re.compile(
                            MultilineTokenDelimiterRegexTemplate.format(
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
    def GetDynamicContent(
        self,
        node: Node,
    ) -> Optional[GrammarPhrase.GetDynamicContentResult]:
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

        # The last line should be empty, as it should be the indentation and footer
        if lines[-1]:
            raise InvalidMultilineFooterError.FromNode(leaf, self.Header, self.Footer, len(lines))

        lines.pop()

        value = "\n".join(lines)
        if not value:
            raise InvalidMultilineContentError.FromNode(leaf)

        value = value.replace("\\{}".format(self.Footer), self.Footer)

        object.__setattr__(node, "_multiline_content", (leaf, value))
        return self._GetDynamicContentImpl(node, leaf, value)

    # ----------------------------------------------------------------------
    @classmethod
    def GetMultilineContent(
        cls,
        node: Node,
    ) -> Tuple[Leaf, str]:
        return getattr(node, "_multiline_content")

    # ----------------------------------------------------------------------
    @Interface.override
    def ExtractParserInfo(
        self,
        node: Node,
    ) -> Union[
        None,
        ParserInfo,
        Callable[[], ParserInfo],
    ]:
        # No parser info, as multi-line statements will never be consumed by the parser
        return None

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.abstractmethod
    def _GetDynamicContentImpl(
        node: Node,
        leaf: Leaf,
        value: str,
    ) -> Optional[GrammarPhrase.GetDynamicContentResult]:
        """Returns any dynamic content that results from the value extracted from the multiline statement"""
        raise Exception("Abstract method")  # pragma: no cover
