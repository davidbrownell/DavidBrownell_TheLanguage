# ----------------------------------------------------------------------
# |
# |  NormalizedIterator.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-04-11 12:32:03
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

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

from Normalize import LineInfo, NormalizedContent

# ----------------------------------------------------------------------
class NormalizedIterator(NormalizedContent):
    """Object used to iterate through content generated via a call to `Normalize`"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        normalized_content: NormalizedContent,
    ):
        super(NormalizedIterator, self).__init__(
            normalized_content.Content,
            normalized_content.ContentLen,
            normalized_content.LineInfos,
        )

        self._line_info_index               = 0
        self._offset                        = 0

    # ----------------------------------------------------------------------
    @property
    def Line(self) -> int:
        """Returns the current (1-based) line number"""
        return self._line_info_index + (0 if self.HasTrailingDedents() and self.AtEnd() else 1)

    @property
    def Column(self) -> int:
        """Returns the current (1-based) column number"""
        if self.AtEnd():
            return 1

        return self._offset - self.LineInfo.OffsetStart + 1

    @property
    def LineInfo(self) -> LineInfo:
        """Returns the current LineInfo object"""
        assert not self.AtEnd()
        return self.LineInfos[self._line_info_index]

    @property
    def Offset(self) -> int:
        """Returns the current offset"""
        return self._offset

    # ----------------------------------------------------------------------
    def AtEnd(self) -> bool:
        return self._line_info_index == len(self.LineInfos)

    # ----------------------------------------------------------------------
    def HasTrailingDedents(self) -> bool:
        return bool(
            self.LineInfos
            and self.LineInfos[-1].HasNewDedents()
            and self.LineInfos[-1].OffsetStart == self.LineInfos[-1].OffsetEnd
            and self.LineInfos[-1].OffsetStart == self.LineInfos[-1].StartPos
            and self.LineInfos[-1].OffsetEnd == self.LineInfos[-1].EndPos
        )

    # ----------------------------------------------------------------------
    def IsBlankLine(self) -> bool:
        """Returns True if the offset is positioned at the beginning of a blank line"""

        # We don't have any line when we are at the end, so we can't have
        # a blank line.
        if self.AtEnd():
            return False

        offset = self.Offset
        info = self.LineInfo

        assert offset == info.OffsetStart
        return info.EndPos == info.StartPos

    # ----------------------------------------------------------------------
    def SkipLine(self) -> "NormalizedIterator":
        info = self.LineInfo

        assert self.Offset == info.OffsetStart

        self._offset = info.OffsetEnd
        return self.Advance(1)

    # ----------------------------------------------------------------------
    def SkipPrefix(self) -> "NormalizedIterator":
        offset = self.Offset
        info = self.LineInfo

        assert offset == info.OffsetStart

        delta = info.StartPos - info.OffsetStart
        if delta == 0:
            return self

        return self.Advance(delta)

    # ----------------------------------------------------------------------
    def SkipSuffix(self) -> "NormalizedIterator":
        offset = self.Offset
        info = self.LineInfo

        assert offset == info.EndPos

        delta = info.OffsetEnd - info.EndPos
        if delta == 0:
            return self

        return self.Advance(delta)

    # ----------------------------------------------------------------------
    def Advance(
        self,
        delta: int,
    ) -> "NormalizedIterator":
        info = self.LineInfo
        offset = self.Offset

        if offset == info.OffsetEnd:
            if (
                self._line_info_index + 1 == len(self.LineInfos)
                and self.HasTrailingDedents()
            ):
                assert delta == 0, delta
            else:
                assert delta == 1, delta

            if not self.AtEnd():
                self._line_info_index += 1

        else:
            assert offset >= info.OffsetStart and offset <= info.OffsetEnd, (offset, info)
            assert offset + delta <= info.OffsetEnd, (delta, offset, info)
            assert (
                offset >= info.StartPos
                or (offset == info.OffsetStart and offset + delta == info.StartPos)
            ), (offset, info)
            assert (
                offset < info.EndPos
                or (offset == info.EndPos and offset + delta == info.OffsetEnd)
            ), (offset, info)

        self._offset += delta

        return self

    # ----------------------------------------------------------------------
    def Clone(self) -> "NormalizedIterator":
        result = self.__class__(self)

        result._offset = self._offset                                       # <Access to a protected member> pylint: disable=W0212
        result._line_info_index = self._line_info_index                     # <Access to a protected member> pylint: disable=W0212

        return result
