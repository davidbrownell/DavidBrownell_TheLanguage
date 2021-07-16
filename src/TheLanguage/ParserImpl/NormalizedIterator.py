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

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Normalize import LineInfo, NormalizedContent

# ----------------------------------------------------------------------
class NormalizedIterator(object):
    """Object used to iterate through content generated via a call to `Normalize`"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        normalized_content: NormalizedContent,
    ):
        self.Content                        = normalized_content.Content
        self.ContentLen                     = normalized_content.ContentLen
        self.LineInfos                      = normalized_content.LineInfos

        self._line_info_index               = 0
        self._offset                        = 0

        self._last_consumed_dedent_line     = None
        self._consumed_dedent_count         = None

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # ----------------------------------------------------------------------
    def __str__(self):
        return "{offset} {content_len} {line_index} {last_consumed_dedent_line} {consumed_dedent_count}".format(
            content_len=self.ContentLen,
            line_index=self._line_info_index,
            offset=self._offset,
            last_consumed_dedent_line=self._last_consumed_dedent_line,
            consumed_dedent_count=self._consumed_dedent_count,
        )

    # ----------------------------------------------------------------------
    def Clone(self):
        # Dynamically created the NormalizedContent object
        result = self.__class__(
            NormalizedContent(
                self.Content,
                self.ContentLen,
                self.LineInfos,
            ),
        )

        result._offset = self._offset                                           # <Access to a protected member> pylint: disable=W0212
        result._line_info_index = self._line_info_index                         # <Access to a protected member> pylint: disable=W0212
        result._last_consumed_dedent_line = self._last_consumed_dedent_line     # <Access to a protected member> pylint: disable=W0212
        result._consumed_dedent_count = self._consumed_dedent_count

        return result

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
    def AtTrailingDedents(self) -> bool:
        return self.HasTrailingDedents() and self._line_info_index == len(self.LineInfos) - 1

    # ----------------------------------------------------------------------
    def HasConsumedAllDedents(self):
        """\
        Returns True if the dedents on the current line have been consumed.

        Dedents on lines without a prefix are troublesome, as there isn't any
        way to indicate that they have already been consumed. Because of this,
        we can find ourselves in an infinite loop when attempting to consume
        a dedent like this over and over.

        Maintain the line of the last dedent consumed so that we can determine
        if the dedent should be ignored.
        """

        return (
            not self.LineInfo.HasNewDedents()
            or (
                self._last_consumed_dedent_line == self._line_info_index
                and self._consumed_dedent_count == self.LineInfo.NumDedents()
            )
        )

    # ----------------------------------------------------------------------
    def ConsumeDedent(self):
        assert self.LineInfo.HasNewDedents()
        if self._last_consumed_dedent_line != self._line_info_index:
            self._last_consumed_dedent_line = self._line_info_index
            self._consumed_dedent_count = 0
        else:
            assert isinstance(self._consumed_dedent_count, int), self._consumed_dedent_count

        self._consumed_dedent_count += 1

    # ----------------------------------------------------------------------
    def IsBlankLine(self) -> bool:
        """Returns True if the offset is positioned at the beginning of a blank line"""

        # We don't have any line when we are at the end, so we can't have
        # a blank line.
        if self.AtEnd():
            return False

        # The trailing dedents line should not be considered a blank line
        if (
            self._line_info_index == len(self.LineInfos) - 1
            and self.HasTrailingDedents()
        ):
            return False

        info = self.LineInfo
        return info.EndPos == info.StartPos

    # ----------------------------------------------------------------------
    def SkipLine(self):
        info = self.LineInfo

        self._offset = info.OffsetEnd

        return self.Advance(1)

    # ----------------------------------------------------------------------
    def SkipPrefix(self):
        offset = self.Offset
        info = self.LineInfo

        assert offset == info.OffsetStart

        delta = info.StartPos - info.OffsetStart
        if delta == 0:
            return self

        return self.Advance(delta)

    # ----------------------------------------------------------------------
    def SkipSuffix(self):
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
    ):
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
                or (delta == info.OffsetEnd - info.OffsetStart)
            ), (offset, info)

        self._offset += delta

        return self
