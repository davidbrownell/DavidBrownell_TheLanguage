# ----------------------------------------------------------------------
# |
# |  NormalizedIterator.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-08-29 12:03:34
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NormalizedIterator object"""

import os

from enum import auto, Enum
from typing import cast, List, Optional

import CommonEnvironment

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Normalize import LineInfo, NormalizedContent


# ----------------------------------------------------------------------
class NormalizedIterator(object):
    """Object used to iterate through content generated via calls to `Normalize`"""

    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class TokenType(Enum):
        Dedent                              = auto()
        Indent                              = auto()
        WhitespacePrefix                    = auto()
        Content                             = auto()
        WhitespaceSuffix                    = auto()
        EndOfLine                           = auto()
        EndOfFile                           = auto()

        # ----------------------------------------------------------------------
        def __eq__(self, other):
            return self.value == other.value

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    @classmethod
    def FromNormalizedContent(
        cls,
        normalized_content: NormalizedContent,
    ) -> "NormalizedIterator":
        return NormalizedIterator(
            normalized_content.Content,
            normalized_content.ContentLen,
            normalized_content.LineInfos,
            normalized_content.Hash,
        )

    # ----------------------------------------------------------------------
    def __init__(
        self,
        content: str,
        content_len: int,
        line_infos: List[LineInfo],
        content_hash: bytes,
    ):
        self.Content                        = content
        self.ContentLen                     = content_len
        self.LineInfos                      = line_infos
        self.Hash                           = content_hash

        self._line_info_index               = 0
        self._offset                        = 0

        self._consumed_dedent_line_index: Optional[int] = None
        self._consumed_dedent_count: Optional[int]      = None

    # ----------------------------------------------------------------------
    def Clone(self) -> "NormalizedIterator":
        result = NormalizedIterator(
            self.Content,
            self.ContentLen,
            self.LineInfos,
            self.Hash,
        )

        result._line_info_index = self._line_info_index
        result._offset = self._offset

        result._consumed_dedent_line_index = self._consumed_dedent_line_index
        result._consumed_dedent_count = self._consumed_dedent_count

        return result

    # ----------------------------------------------------------------------
    def ToCacheKey(self):
        return (
            self.Hash,
            self._offset,

            # Note that Offset is not enough to determine uniqueness, as there are degrees of dedent
            # consumption.
            self._consumed_dedent_line_index,
            self._consumed_dedent_count,
        )

    # ----------------------------------------------------------------------
    def __repr__(self):
        return "[{}, {}] ({})".format(self.Line, self.Column, self.Offset)

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        return (
            self.Hash == other.Hash
            and self._offset == other._offset
            and self._consumed_dedent_line_index == other._consumed_dedent_line_index
            and self._consumed_dedent_count == other._consumed_dedent_count
        )

    # ----------------------------------------------------------------------
    @property
    def Offset(self) -> int:
        return self._offset

    @property
    def LineInfo(self) -> LineInfo:
        assert not self.AtEnd()
        return self.LineInfos[self._line_info_index]

    @property
    def Line(self) -> int:
        """Returns the current (1-based) line number"""
        return self._line_info_index + 1

    @property
    def Column(self) -> int:
        """Returns the current (1-based) column number"""
        if self.AtEnd():
            return 1

        return self._offset - self.LineInfo.OffsetStart + 1

    # ----------------------------------------------------------------------
    def AtEnd(self) -> bool:
        if self._line_info_index == len(self.LineInfos):
            return True

        if (
            self.HasEndOfFileDedents()
            and self._line_info_index == len(self.LineInfos) - 1
            and self._consumed_dedent_line_index == self._line_info_index
            and self._consumed_dedent_count == self.LineInfos[-1].NumDedents
        ):
            return True

        return False

    # ----------------------------------------------------------------------
    def GetNextToken(self) -> "NormalizedIterator.TokenType":
        if self.AtEnd():
            return NormalizedIterator.TokenType.EndOfFile

        line_info = self.LineInfo

        if (
            line_info.NumDedents is not None
            and (
                self._consumed_dedent_line_index != self._line_info_index
                or self._consumed_dedent_count != line_info.NumDedents
            )
        ):
            return NormalizedIterator.TokenType.Dedent

        if self._offset < line_info.PosStart:
            if line_info.NewIndentationValue is not None:
                return NormalizedIterator.TokenType.Indent
            else:
                return NormalizedIterator.TokenType.WhitespacePrefix

        if self._offset < line_info.PosEnd:
            return NormalizedIterator.TokenType.Content

        if self._offset >= line_info.PosEnd and self._offset < line_info.OffsetEnd:
            return NormalizedIterator.TokenType.WhitespaceSuffix

        if self._offset == line_info.OffsetEnd:
            return NormalizedIterator.TokenType.EndOfLine

        assert False, self._offset

    # ----------------------------------------------------------------------
    def HasEndOfFileDedents(self) -> bool:
        return (
            bool(self.LineInfos)
            and self.LineInfos[-1].NumDedents is not None
            and cast(int, self.LineInfos[-1].NumDedents) > 0
            and self.LineInfos[-1].OffsetStart == self.LineInfos[-1].OffsetEnd
            and self.LineInfos[-1].PosStart == self.LineInfos[-1].OffsetStart
            and self.LineInfos[-1].PosEnd == self.LineInfos[-1].OffsetEnd
        )

    # ----------------------------------------------------------------------
    def ConsumeDedent(self):
        assert self.LineInfo.NumDedents is not None
        assert self._offset == self.LineInfo.OffsetStart

        if self._consumed_dedent_line_index != self._line_info_index:
            self._consumed_dedent_line_index = self._line_info_index
            self._consumed_dedent_count = 0
        else:
            assert isinstance(self._consumed_dedent_count, int)

        self._consumed_dedent_count += 1

    # ----------------------------------------------------------------------
    def IsBlankLine(self) -> bool:
        """Returns True if the offset is positioned at the beginning of a blank line"""

        # We don't have a line when we are at the end, so it can't be a blank line by definition
        if self.AtEnd():
            return False

        # The trailing dedent lines should not be considered blank lines
        if (
            self._line_info_index == len(self.LineInfos) - 1
            and self.HasEndOfFileDedents()
        ):
            return False

        line_info = self.LineInfo
        return line_info.PosEnd == line_info.PosStart

    # ----------------------------------------------------------------------
    def SkipLine(self) -> "NormalizedIterator":
        self._offset = self.LineInfo.OffsetEnd

        # Move past the newline
        return self.Advance(1)

    # ----------------------------------------------------------------------
    def SkipWhitespacePrefix(self) -> "NormalizedIterator":
        offset = self.Offset
        line_info = self.LineInfo

        assert offset == line_info.OffsetStart

        delta = line_info.PosStart - line_info.OffsetStart
        if delta == 0:
            return self

        return self.Advance(delta)

    # ----------------------------------------------------------------------
    def SkipWhitespaceSuffix(self) -> "NormalizedIterator":
        offset = self.Offset
        line_info = self.LineInfo

        assert offset == line_info.PosEnd

        delta = line_info.OffsetEnd - line_info.PosEnd
        if delta == 0:
            return self

        return self.Advance(delta)

    # ----------------------------------------------------------------------
    def Advance(
        self,
        delta: int,
    ) -> "NormalizedIterator":
        assert self.AtEnd() == False

        offset = self.Offset
        line_info = self.LineInfo

        if offset == line_info.OffsetEnd:
            assert delta == 1, delta
            assert self.GetNextToken() == NormalizedIterator.TokenType.EndOfLine, self.GetNextToken()
            self._line_info_index += 1

        else:
            assert offset >= line_info.OffsetStart and offset <= line_info.OffsetEnd, (offset, line_info)
            assert offset + delta <= line_info.OffsetEnd, (delta, offset, line_info)
            assert (
                offset >= line_info.PosStart
                or (
                    offset == line_info.OffsetStart
                    and (
                        offset + delta == line_info.PosStart
                        or delta == line_info.OffsetEnd - line_info.OffsetStart
                    )
                )
            ), (offset, line_info)

        self._offset += delta

        return self
