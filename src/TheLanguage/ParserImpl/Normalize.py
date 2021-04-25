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

from collections import namedtuple

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

from Error import CreateErrorClass

# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
InvalidTabsAndSpacesNormalizeException      = CreateErrorClass("The tabs and/or spaces used to indent this line differ from the tabs and/or spaces used on previous lines")
InvalidIndentationNormalizeException        = CreateErrorClass("The unindent level on this line does not match any outer indentation level")


# ----------------------------------------------------------------------
class LineInfo(object):
    """Information about a line"""

    # ----------------------------------------------------------------------
    class IndentType(enum.Enum):
        Indent                              = enum.auto()
        Dedent                              = enum.auto()

    # ----------------------------------------------------------------------
    def __init__(
        self,
        offset_start: int,
        offset_end: int,
        startpos: int,
        endpos: int,
        indentation_info: Optional[
            Tuple[
                IndentType,
                int,                        # When...
                                            #   Indent: indentation value
                                            #   Dedent: number of dedents
            ]
        ]
    ):
        assert offset_start >= 0, offset_start
        assert offset_end >= offset_start, (offset_start, offset_end)
        assert startpos >= offset_start, (startpos, offset_start)
        assert endpos <= offset_end, (endpos, offset_end)
        assert endpos >= startpos, (startpos, endpos)

        self.OffsetStart                    = offset_start
        self.OffsetEnd                      = offset_end

        self.StartPos                       = startpos
        self.EndPos                         = endpos

        self.IndentationInfo                = indentation_info

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

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
class NormalizedContent(object):
    """Data returned from calls to the function `Normalize`"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        content: str,
        content_len: int,
        line_infos: List[LineInfo],
    ):
        assert content
        assert content_len
        assert line_infos

        self.Content                        = content
        self.ContentLen                     = content_len
        self.LineInfos                      = line_infos

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


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
    IndentationInfo                         = namedtuple("IndentationInfo", ["num_chars", "value"])

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
                                raise InvalidTabsAndSpacesNormalizeException(
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
                                raise InvalidIndentationNormalizeException(
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
