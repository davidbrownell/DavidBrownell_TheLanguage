# ----------------------------------------------------------------------
# |
# |  DocstringStatement.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-29 06:25:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the DocstringStatement object"""

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
    from ..Common import Tokens as CommonTokens
    from ...GrammarPhrase import GrammarPhrase, ValidationError
    from ....Components.Token import RegexToken

    from ....Phrases.DSL import (
        CreatePhrase,
        ExtractSequence,
        ExtractToken,
        Leaf,
        Node,
        PhraseItem,
    )


# ----------------------------------------------------------------------
_HEADER                                     = "<<<"
_FOOTER                                     = ">>>"


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDocstringHeaderError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("The header ('{}') must be followed by a new line.".format(_HEADER))

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Leaf,
    ):
        return cls(
            node.IterBegin.Line,
            node.IterBegin.Column,
            node.IterBegin.Line,
            node.IterBegin.Column + len(_HEADER),
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDocstringFooterError(ValidationError):
    LineOffset: int

    MessageTemplate                         = Interface.DerivedProperty("The footer ('{}') must be aligned vertically with the header ('{}') [Docstring line {{LineOffset}}].".format(_FOOTER, _HEADER))

    # ----------------------------------------------------------------------
    @classmethod
    def FromNode(
        cls,
        node: Leaf,
        line_offset: int,
    ):
        return cls(
            node.IterEnd.Line,
            node.IterEnd.Column - len(_FOOTER),
            node.IterEnd.Line,
            node.IterEnd.Column,
            line_offset,
        )


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDocstringIndentError(ValidationError):
    LineOffset: int

    MessageTemplate                         = Interface.DerivedProperty("Docstring content must be aligned vertically with the header ('{}') [Docstring line {{LineOffset}}].".format(_HEADER))


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidDocstringContentError(ValidationError):
    MessageTemplate                         = Interface.DerivedProperty("Docstrings cannot be empty.")


# ----------------------------------------------------------------------
class DocstringStatement(GrammarPhrase):
    """\
    Documentation for a parent node.

    '<<<'
    <content>
    '>>>'

    Examples:
        <<<
        This is a docstring with one line.
        >>>

        <<<
        This is a
        multi-line
        docstring.
        >>>
    """

    PHRASE_NAME                             = "Docstring Statement"

    # ----------------------------------------------------------------------
    def __init__(self):
        super(DocstringStatement, self).__init__(
            GrammarPhrase.Type.Statement,
            CreatePhrase(
                name=self.PHRASE_NAME,
                item=[
                    RegexToken(
                        "Docstring",
                        re.compile(
                            r"{}(?P<value>.+?)(?<!\\){}".format(re.escape(_HEADER), re.escape(_FOOTER)),
                            re.DOTALL | re.MULTILINE,
                        ),
                        is_multiline=True,
                    ),

                    CommonTokens.Newline,
                ],
            ),
        )

    # ----------------------------------------------------------------------
    @staticmethod
    @Interface.override
    def ValidateNodeSyntax(
        node: Node,
    ) -> Optional[bool]:
        nodes = ExtractSequence(node)
        assert len(nodes) == 2

        leaf = cast(Leaf, nodes[0])
        value = cast(str, ExtractToken(leaf))

        if not value.startswith("\n"):
            raise InvalidDocstringHeaderError.FromNode(leaf)
        value = value[1:]

        lines = value.split("\n")

        expected_indentation_len = leaf.IterBegin.Offset - leaf.IterBegin.LineInfo.OffsetStart

        if expected_indentation_len:
            expected_indentation = leaf.IterBegin.Content[leaf.IterBegin.Offset - expected_indentation_len : leaf.IterBegin.Offset]

            for line_index, line in enumerate(lines):
                if not line.startswith(expected_indentation):
                    raise InvalidDocstringIndentError.FromNode(leaf, line_index + 1)

                lines[line_index] = line[expected_indentation_len:]

        # The last line should be empty, as should have had the prefix and footer
        if lines[-1]:
            raise InvalidDocstringFooterError.FromNode(leaf, len(lines))

        lines.pop()

        value = "\n".join(lines)
        if not value:
            raise InvalidDocstringContentError.FromNode(leaf)

        # Persist the info
        object.__setattr__(node, "Info", value)
