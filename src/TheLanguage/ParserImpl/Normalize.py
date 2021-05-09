# ----------------------------------------------------------------------
# |
# |  Normalize.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-09 07:17:22
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types and functions that normalize source content"""

import enum
import os

from typing import List, Optional, Tuple

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Error import Error

# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTabsAndSpacesNormalizeError(Error):
    MessageTemplate                         = Interface.DerivedProperty("The tabs and/or spaces used to indent this line differ from the tabs and/or spaces used on previous lines")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidIndentationNormalizeError(Error):
    MessageTemplate                         = Interface.DerivedProperty("The unindent level on this line does not match any outer indentation level")


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class LineInfo(object):
    """Information about a line"""

    # ----------------------------------------------------------------------
    class IndentType(enum.Enum):
        Indent                              = enum.auto()
        Dedent                              = enum.auto()

    # ----------------------------------------------------------------------
    OffsetStart: int
    OffsetEnd: int

    StartPos: int
    EndPos: int

    IndentationInfo: Optional[
        Tuple[
            IndentType,
            int,                            # When...
                                            #   Indent: indentation value
                                            #   Dedent: number of dedents
        ]
    ]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.OffsetStart >= 0, self
        assert self.OffsetEnd >= self.OffsetStart, self
        assert self.StartPos >= self.OffsetStart, self
        assert self.EndPos <= self.OffsetEnd, self
        assert self.EndPos >= self.StartPos, self

    # ----------------------------------------------------------------------
    def HasWhitespacePrefix(self):
        return self.StartPos > self.OffsetStart

    # ----------------------------------------------------------------------
    def HasWhitespaceSuffix(self):
        return self.EndPos < self.OffsetEnd

    # ----------------------------------------------------------------------
    def HasNewIndent(self):
        return self.IndentationInfo is not None and self.IndentationInfo[0] == LineInfo.IndentType.Indent

    # ----------------------------------------------------------------------
    def HasNewDedents(self):
        return self.IndentationInfo is not None and self.IndentationInfo[0] == LineInfo.IndentType.Dedent

    # ----------------------------------------------------------------------
    def IndentationValue(self):
        return self.IndentationInfo[1] if self.HasNewIndent() else None

    # ----------------------------------------------------------------------
    def NumDedents(self):
        return self.IndentationInfo[1] if self.HasNewDedents() else 0


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NormalizedContent(object):
    """Data returned from calls to the function `Normalize`"""

    Content: str
    ContentLen: int
    LineInfos: List[LineInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Content
        assert self.ContentLen
        assert self.LineInfos


# ----------------------------------------------------------------------
# |
# |  Public Methods
# |
# ----------------------------------------------------------------------
def Normalize(
    content: str,
) -> NormalizedContent:
    """\
    Normalizes the provided content to prevent repeated calculations.

    Note that all content is preserved with the following exceptions:
        - Trailing whitespace is ignored ("line end   \n" -> "line end\n")
        - Whitespace in a blank line is ignored ("    \n" -> "\n")
    """

    # ----------------------------------------------------------------------
    @dataclass
    class IndentationInfo(object):
        num_chars: int
        value: int

    # ----------------------------------------------------------------------

    assert content

    if content[-1] != "\n":
        content += "\n"

    len_content = len(content)
    offset = 0

    line_infos: List[LineInfo] = []
    indentation_stack = [IndentationInfo(0, 0)]

    # ----------------------------------------------------------------------
    def CreateLineInfo():
        nonlocal len_content
        nonlocal offset

        line_start_offset = offset
        line_end_offset: Optional[int] = None

        indentation_value = 0
        new_indentation_value: Optional[int] = None
        num_dedents = 0

        content_start_offset: Optional[int] = None
        content_end_offset: Optional[int] = None

        while offset < len_content:
            char = content[offset]

            if indentation_value is not None:
                if char == " ":
                    indentation_value += 1
                elif char == "\t":
                    # Ensure that " \t" compares as different from "\t "
                    indentation_value += (offset - line_start_offset + 1) * 100
                else:
                    assert char == "\n" or not char.isspace(), char

                    if char != "\n":
                        num_chars = offset - line_start_offset

                        if num_chars:
                            # Ensure that the whitespace prefix for this line uses the same
                            # mix of tabs and spaces.
                            if (
                                num_chars == indentation_stack[-1].num_chars
                                and indentation_value != indentation_stack[-1].value
                            ):
                                raise InvalidTabsAndSpacesNormalizeError(
                                    len(line_infos) + 1,
                                    offset - line_start_offset + 1,
                                )

                            # Detect indents
                            if num_chars > indentation_stack[-1].num_chars:
                                indentation_stack.append(IndentationInfo(num_chars, indentation_value))
                                new_indentation_value = indentation_value

                        # Detect dedents
                        while num_chars < indentation_stack[-1].num_chars:
                            indentation_stack.pop()
                            num_dedents += 1

                            if num_chars > indentation_stack[-1].num_chars:
                                raise InvalidIndentationNormalizeError(
                                    len(line_infos) + 1,
                                    offset - line_start_offset + 1,
                                )

                    indentation_value = None
                    content_start_offset = offset

            if char == "\n":
                line_end_offset = offset
                offset += 1

                # Remove trailing whitespace
                content_end_offset = line_end_offset

                assert content_start_offset is not None
                while content_end_offset > content_start_offset and content[content_end_offset - 1].isspace():
                    content_end_offset -= 1

                break

            offset += 1

        assert line_end_offset is not None
        assert content_start_offset is not None
        assert content_end_offset is not None

        if isinstance(new_indentation_value, int):
            indentation_info = (LineInfo.IndentType.Indent, new_indentation_value)
        elif num_dedents:
            indentation_info = (LineInfo.IndentType.Dedent, num_dedents)
        else:
            indentation_info = None

        return LineInfo(
            line_start_offset,
            line_end_offset,
            content_start_offset,
            content_end_offset,
            indentation_info,
        )

    # ----------------------------------------------------------------------

    while offset < len_content:
        line_infos.append(CreateLineInfo())

    if len(indentation_stack) > 1:
        line_infos.append(
            LineInfo(
                offset,
                offset,
                offset,
                offset,
                (LineInfo.IndentType.Dedent, len(indentation_stack) - 1),
            ),
        )

    return NormalizedContent(
        content,
        len_content,
        line_infos,
    )
