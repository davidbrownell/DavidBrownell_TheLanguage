# ----------------------------------------------------------------------
# |
# |  Normalize.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-07 22:59:16
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

from enum import auto, Enum
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
    # |  Public Types
    class IndentType(Enum):
        Indent                              = auto()
        Dedent                              = auto()

    # ----------------------------------------------------------------------
    # |  Public Data
    OffsetStart: int
    OffsetEnd: int

    PosStart: int
    PosEnd: int

    IndentationLevel: int                   # 0-based relative level (not the actual indentation size)

    IndentationInfo: Optional[
        Tuple[
            IndentType,
            int,                            # When...
                                            #   Indent: indentation value
                                            #   Dedent: number of dedents
        ]
    ]

    # ----------------------------------------------------------------------
    # |  Public Methods
    def __post_init__(self):
        assert self.OffsetStart >= 0, self
        assert self.OffsetEnd >= self.OffsetStart, self
        assert self.PosStart >= self.OffsetStart, self
        assert self.PosEnd >= self.PosStart, self
        assert self.PosEnd <= self.OffsetEnd, self
        assert self.IndentationLevel >= 0, self

    # ----------------------------------------------------------------------
    def HasWhitespacePrefix(self):
        return self.PosStart > self.OffsetStart

    # ----------------------------------------------------------------------
    def HasWhitespaceSuffix(self):
        return self.PosEnd < self.OffsetEnd

    # ----------------------------------------------------------------------
    def HasNewIndent(self):
        return self.IndentationInfo is not None and self.IndentationInfo[0] == LineInfo.IndentType.Indent

    # ----------------------------------------------------------------------
    def HasNewDedents(self):
        return self.IndentationInfo is not None and self.IndentationInfo[0] == LineInfo.IndentType.Dedent

    # ----------------------------------------------------------------------
    def IndentationValue(self) -> Optional[int]:
        if not self.HasNewIndent():
            return None

        assert self.IndentationInfo
        return self.IndentationInfo[1]

    # ----------------------------------------------------------------------
    def NumDedents(self) -> int:
        if not self.HasNewDedents():
            return 0

        assert self.IndentationInfo
        return self.IndentationInfo[1]


# ----------------------------------------------------------------------
@dataclass(frozen=True, unsafe_hash=True)
class NormalizedContent(object):
    """Data returned from calls to the function `Normalize`"""

    Content: str
    ContentLen: int
    LineInfos: List[LineInfo]

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Content, self
        assert self.ContentLen, self
        assert self.LineInfos, self


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def Normalize(
    content: str,
) -> NormalizedContent:
    """Normalizes the provided content to prevent repeated calculations"""

    # ----------------------------------------------------------------------
    @dataclass
    class IndentationInfo(object):
        num_chars: int
        value: int

    # ----------------------------------------------------------------------

    if not content or content[-1] != "\n":
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
            character = content[offset]

            if indentation_value is not None:
                if character == " ":
                    indentation_value += 1
                elif character == "\t":
                    # Ensure that " \t" compares as different from "\t "
                    indentation_value += (offset - line_start_offset + 1) * 100
                else:
                    assert character == "\n" or not character.isspace(), character

                    if character != "\n":
                        num_chars = offset - line_start_offset

                        if num_chars:
                            # Ensure that the whitespace prefix for this line uses the same max of
                            # tabs and spaces as the indentation associated with the previous line.
                            if (
                                num_chars == indentation_stack[-1].num_chars
                                and indentation_value != indentation_stack[-1].value
                            ):
                                raise InvalidTabsAndSpacesNormalizeError(
                                    len(line_infos) + 1,
                                    offset - line_start_offset + 1,
                                )

                            # Dedent indents
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

            if character == "\n":
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
            assert num_dedents == 0, num_dedents
            indentation_info = (LineInfo.IndentType.Indent, new_indentation_value)
        elif num_dedents:
            assert new_indentation_value is None, new_indentation_value
            indentation_info = (LineInfo.IndentType.Dedent, num_dedents)
        else:
            indentation_info = None

        return LineInfo(
            line_start_offset,
            line_end_offset,
            content_start_offset,
            content_end_offset,
            len(indentation_stack) - 1,
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
                0,
                (LineInfo.IndentType.Dedent, len(indentation_stack) - 1),
            ),
        )

    return NormalizedContent(
        content,
        len_content,
        line_infos,
    )
