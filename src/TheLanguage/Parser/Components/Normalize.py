# ----------------------------------------------------------------------
# |
# |  Normalize.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-29 09:25:30
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

import hashlib
import os

from typing import List, Optional

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
    from .Error import Error


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class InvalidTabsAndSpacesNormalizeError(Error):
    MessageTemplate                         = Interface.DerivedProperty("The spaces and/or tabs used to indent this line differ from the spaces and/or tabs used on previous lines.")


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LineInfo(YamlRepr.ObjectReprImplBase):
    """Information about a line"""

    OffsetStart: int
    OffsetEnd: int

    PosStart: int
    PosEnd: int

    NumDedents: Optional[int]               = field(default=None)
    NewIndentationValue: Optional[int]      = field(default=None)

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.OffsetStart >= 0, self
        assert self.OffsetEnd >= self.OffsetStart, self
        assert self.PosStart >= self.OffsetStart, self
        assert self.PosEnd >= self.PosStart, self
        assert self.PosEnd <= self.OffsetEnd, self
        assert self.NumDedents is None or self.NumDedents > 0, self
        assert self.NewIndentationValue is None or self.NewIndentationValue > 0, self

    # ----------------------------------------------------------------------
    def HasWhitespacePrefix(self):
        return self.PosStart != self.OffsetStart

    # ----------------------------------------------------------------------
    def HasContent(self):
        return self.PosStart != self.PosEnd

    # ----------------------------------------------------------------------
    def HasWhitespaceSuffix(self):
        return self.PosEnd != self.OffsetEnd


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class NormalizedContent(object):
    """Data returned from calls to `Normalize`"""

    Content: str
    ContentLen: int
    LineInfos: List[LineInfo]
    Hash: bytes                             = field(default=None)  # type: ignore

    # ----------------------------------------------------------------------
    def __post_init__(self):
        assert self.Content, self
        assert self.ContentLen, self
        assert self.LineInfos, self

        if self.Hash is None:
            object.__setattr__(self, "Hash", self.CalculateHash(self.Content))

    # ----------------------------------------------------------------------
    @staticmethod
    def CalculateHash(
        content: str,
    ) -> bytes:
        hash = hashlib.sha256()
        hash.update(content.encode("utf-8"))
        return hash.digest()


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
    def CreateLineInfo() -> LineInfo:
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
                    # Ensure that " \t" compares as different from "\t " and that "\t"
                    # compares different from " "
                    indentation_value += (offset - line_start_offset + 1) * 100
                else:
                    assert character == "\n" or not character.isspace(), character

                    num_chars = offset - line_start_offset

                    if character != "\n":
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

                        # Detect dedents
                        while num_chars < indentation_stack[-1].num_chars:
                            indentation_stack.pop()
                            num_dedents += 1

                        # Detect indents
                        if num_chars > indentation_stack[-1].num_chars:
                            indentation_stack.append(IndentationInfo(num_chars, indentation_value))
                            new_indentation_value = indentation_value

                    indentation_value = None
                    content_start_offset = offset

            if character == "\n":
                line_end_offset = offset
                offset += 1

                # Account for the trailing whitespace
                content_end_offset = line_end_offset

                assert content_start_offset is not None
                while content_end_offset > content_start_offset and content[content_end_offset - 1].isspace():
                    content_end_offset -= 1

                break

            offset += 1

        assert line_end_offset is not None
        assert content_start_offset is not None
        assert content_end_offset is not None

        # <Too many positional arguments> pylint: disable=E1121
        return LineInfo(
            line_start_offset,
            line_end_offset,
            content_start_offset,
            content_end_offset,
            NumDedents=num_dedents if num_dedents != 0 else None,
            NewIndentationValue=new_indentation_value,
        )

    # ----------------------------------------------------------------------

    while offset < len_content:
        line_infos.append(CreateLineInfo())

    if len(indentation_stack) > 1:
        line_infos.append(
            # <Too many positional arguments> pylint: disable=E1121
            LineInfo(
                offset,
                offset,
                offset,
                offset,
                NumDedents=len(indentation_stack) - 1,
            ),
        )

    return NormalizedContent(content, len_content, line_infos)
