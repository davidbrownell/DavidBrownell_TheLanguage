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

import os

from typing import List, Optional, Tuple

from collections import namedtuple

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

import Error

# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
InvalidTabsAndSpacesNormalizeException      = Error.CreateErrorClass("The tabs and/or spaces used to indent this line differ from the tabs and/or spaces used on previous lines")
InvalidIndentationNormalizeException        = Error.CreateErrorClass("The unindent level on this line does not match any outer indentation level")


# ----------------------------------------------------------------------
class LineInfo(object):
    """Information about a line"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        offset: int,
        new_indentation: Optional[Tuple[int, int]],     # (startpos, endpos)
        num_dedents: int,
        startpos: int,
        endpos: int,
    ):
        assert offset >= 0, offset
        assert new_indentation is None or (new_indentation[0] == offset and new_indentation[-1] >= offset), new_indentation
        assert num_dedents >= 0, num_dedents
        assert startpos >= offset, (startpos, offset)
        assert endpos >= startpos, (startpos, endpos)

        self.Offset                         = offset
        self.NewIndentation                 = new_indentation
        self.NumDedents                     = num_dedents
        self.StartPos                       = startpos
        self.EndPos                         = endpos

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # ----------------------------------------------------------------------
    def __repr__(self):
        return CommonEnvironment.ObjectReprImpl(
            self,
            include_id=False,
        )


# ----------------------------------------------------------------------
class NormalizeResult(object):
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
    def __repr__(self):
        return CommonEnvironment.ObjectReprImpl(
            self,
            include_id=False,
        )


# ----------------------------------------------------------------------
# |
# |  Public Methods
# |
# ----------------------------------------------------------------------
def Normalize(
    content: str,
) -> NormalizeResult:
    """\
    Normalizes the provided content to prevent repeated calculations.

    Note that all content is preserved with the following exceptions:
        - Trailing whitespace is ignored ("line end   \n" -> "line end\n")
        - Whitespace in a blank line is ignored ("    \n" -> "\n")
    """

    # ----------------------------------------------------------------------
    IndentationInfo                         = namedtuple("IndentationInfo", ["num_chars", "value"])

    # ----------------------------------------------------------------------

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
        new_indentation: Optional[Tuple[int, int]] = None
        num_dedents = 0
        content_start_offset: Optional[int] = None

        while offset < len_content:
            char = content[offset]

            if indentation_value is not None:
                if char == " ":
                    indentation_value += 1
                elif char == "\t":
                    # Ensure that " \t" compares as different from "\t "
                    indentation_value += (offset - line_start_offset) * 100
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
                                new_indentation = (line_start_offset, offset)

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
                while line_end_offset > content_start_offset and content[line_end_offset - 1].isspace():
                    line_end_offset -= 1

                break

            offset += 1

        return LineInfo(
            line_start_offset,
            new_indentation,
            num_dedents,
            content_start_offset,
            line_end_offset,
        )

    # ----------------------------------------------------------------------

    while offset < len_content:
        line_infos.append(CreateLineInfo())

    if len(indentation_stack) > 1:
        line_infos.append(LineInfo(offset, None, len(indentation_stack) - 1, offset, offset))

    return NormalizeResult(
        content,
        len_content,
        line_infos,
    )
