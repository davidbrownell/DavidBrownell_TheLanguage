# ----------------------------------------------------------------------
# |
# |  NormalizedIterator.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-10-15 20:03:55
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

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment.InstanceCache import InstanceCache, InstanceCacheGet, InstanceCacheReset

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Normalize import LineInfo, NormalizedContent


# ----------------------------------------------------------------------
def NormalizedIteratorCopyOnWriteDecorator(method):
    # ----------------------------------------------------------------------
    def CopyOnWrite(self, *args, **kwargs):
        if not self._own_impl:
            self._impl = self._impl.Clone()
            self._own_impl = True

        return method(self, *args, **kwargs)

    # ----------------------------------------------------------------------

    return CopyOnWrite


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
        # pylint: disable=too-many-function-args
        self._impl                          = self.__class__.Impl(
            self.__class__.ImmutableContentData(
                content,
                content_len,
                line_infos,
                content_hash,
            ),
            0, 0, None, None,
        )

        self._own_impl                      = True

    # ----------------------------------------------------------------------
    def Clone(self) -> "NormalizedIterator":
        # Avoid __init__
        obj = self.__class__.__new__(self.__class__)
        super(NormalizedIterator, obj).__init__()

        obj._impl = self._impl
        obj._own_impl = False

        self._own_impl = False

        return obj

    # ----------------------------------------------------------------------
    def __eq__(self, other):
        if other is None:
            return False

        return self.ToCacheKey() == other.ToCacheKey()

    # ----------------------------------------------------------------------
    def __repr__(self) -> str:
        return self._impl.Repr()

    # ----------------------------------------------------------------------
    @property
    def Content(self) -> str:
        return self._impl.Data.Content

    @property
    def ContentLen(self) -> int:
        return self._impl.Data.ContentLen

    @property
    def LineInfos(self) -> List[LineInfo]:
        return self._impl.Data.LineInfos

    @property
    def HasEndOfFileDedents(self) -> bool:
        return self._impl.Data.HasEndOfFileDedents

    @property
    def Offset(self) -> int:
        return self._impl.offset

    @property
    def LineInfo(self) -> LineInfo:
        return self._impl.LineInfo

    @property
    def Line(self) -> int:
        return self._impl.Line

    @property
    def Column(self) -> int:
        return self._impl.Column

    # ----------------------------------------------------------------------
    def ToCacheKey(self):
        return self._impl.ToCacheKey()

    # ----------------------------------------------------------------------
    def AtEnd(self) -> bool:
        return self._impl.AtEnd()

    # ----------------------------------------------------------------------
    def GetNextTokenType(self) -> "NormalizedIterator.TokenType":
        return self._impl.GetNextTokenType()

    # ----------------------------------------------------------------------
    def IsBlankLine(self) -> bool:
        return self._impl.IsBlankLine()

    # ----------------------------------------------------------------------
    @NormalizedIteratorCopyOnWriteDecorator
    def ConsumeDedent(self) -> None:
        if not self._own_impl:
            self._impl = self._impl.Clone()
            self._own_impl = True

        self._impl.ConsumeDedent()

    # ----------------------------------------------------------------------
    @NormalizedIteratorCopyOnWriteDecorator
    def SkipLine(self) -> "NormalizedIterator":
        self._impl.SkipLine()
        return self

    # ----------------------------------------------------------------------
    @NormalizedIteratorCopyOnWriteDecorator
    def SkipWhitespacePrefix(self) -> "NormalizedIterator":
        self._impl.SkipWhitespacePrefix()
        return self

    # ----------------------------------------------------------------------
    @NormalizedIteratorCopyOnWriteDecorator
    def SkipWhitespaceSuffix(self) -> "NormalizedIterator":
        self._impl.SkipWhitespaceSuffix()
        return self

    # ----------------------------------------------------------------------
    @NormalizedIteratorCopyOnWriteDecorator
    def Advance(
        self,
        delta: int,
    ) -> "NormalizedIterator":
        self._impl.Advance(delta)
        return self

    # ----------------------------------------------------------------------
    # |
    # |  Private Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class ImmutableContentData(object):
        Content: str
        ContentLen: int
        LineInfos: List[LineInfo]
        Hash: bytes
        HasEndOfFileDedents: bool           = field(init=False)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            object.__setattr__(
                self,
                "HasEndOfFileDedents",
                (
                    bool(self.LineInfos)
                    and self.LineInfos[-1].NumDedents is not None
                    and cast(int, self.LineInfos[-1].NumDedents) > 0
                    and self.LineInfos[-1].OffsetStart == self.LineInfos[-1].OffsetEnd
                    and self.LineInfos[-1].ContentStart == self.LineInfos[-1].OffsetStart
                    and self.LineInfos[-1].ContentEnd == self.LineInfos[-1].OffsetEnd
                ),
            )

    # ----------------------------------------------------------------------
    @dataclass
    class Impl(InstanceCache):
        Data: "NormalizedIterator.ImmutableContentData"

        line_info_index: int
        offset: int

        consumed_dedent_line_index: Optional[int]
        consumed_dedent_count: Optional[int]

        # ----------------------------------------------------------------------
        def __post_init__(self):
            InstanceCache.__init__(self)

        # ----------------------------------------------------------------------
        @property
        def LineInfo(self):
            return self.Data.LineInfos[self.line_info_index]

        @property
        def Line(self):
            return self.line_info_index + 1

        @property
        def Column(self):
            if self.AtEnd():
                return 1

            return self.offset - self.LineInfo.OffsetStart + 1

        # ----------------------------------------------------------------------
        def Clone(self):
            # pylint: disable=too-many-function-args
            return self.__class__(
                self.Data,
                self.line_info_index,
                self.offset,
                self.consumed_dedent_line_index,
                self.consumed_dedent_count,
            )

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def AtEnd(self) -> bool:
            if self.line_info_index == len(self.Data.LineInfos):
                return True

            if (
                self.Data.HasEndOfFileDedents
                and self.line_info_index == len(self.Data.LineInfos) - 1
                and self.consumed_dedent_line_index == self.line_info_index
                and self.consumed_dedent_count == self.Data.LineInfos[-1].NumDedents
            ):
                return True

            return False

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def ToCacheKey(self):
            return (
                self.Data.Hash,
                self.offset,

                # Note that Offset is not enough to determine uniqueness, as there are degrees of dedent
                # consumption.
                self.consumed_dedent_line_index,
                self.consumed_dedent_count,
            )

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def Repr(self) -> str:
            return "[{}, {}] ({})".format(self.Line, self.Column, self.offset)

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def GetNextTokenType(self) -> "NormalizedIterator.TokenType":
            if self.AtEnd():
                return NormalizedIterator.TokenType.EndOfFile

            line_info = self.LineInfo

            if (
                line_info.NumDedents is not None
                and (
                    self.consumed_dedent_line_index != self.line_info_index
                    or self.consumed_dedent_count != line_info.NumDedents
                )
            ):
                return NormalizedIterator.TokenType.Dedent

            if self.offset < line_info.ContentStart:
                if line_info.NewIndentationValue is not None:
                    return NormalizedIterator.TokenType.Indent

                return NormalizedIterator.TokenType.WhitespacePrefix

            if self.offset < line_info.ContentEnd:
                return NormalizedIterator.TokenType.Content

            if self.offset >= line_info.ContentEnd and self.offset < line_info.OffsetEnd:
                return NormalizedIterator.TokenType.WhitespaceSuffix

            assert self.offset == line_info.OffsetEnd
            return NormalizedIterator.TokenType.EndOfLine

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def IsBlankLine(self) -> bool:
            """Returns True if the offset is positioned at the beginning of a blank line"""

            # We don't have a line when we are at the end, so it can't be a blank line by definition
            if self.AtEnd():
                return False

            # The trailing dedent lines should not be considered blank lines
            if (
                self.line_info_index == len(self.Data.LineInfos) - 1
                and self.Data.HasEndOfFileDedents
            ):
                return False

            line_info = self.LineInfo
            return line_info.ContentEnd == line_info.ContentStart

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def ConsumeDedent(self) -> None:
            assert self.LineInfo.NumDedents is not None
            assert self.offset == self.LineInfo.OffsetStart

            if self.consumed_dedent_line_index != self.line_info_index:
                self.consumed_dedent_line_index = self.line_info_index
                self.consumed_dedent_count = 0
            else:
                assert isinstance(self.consumed_dedent_count, int)

            self.consumed_dedent_count += 1

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def SkipLine(self) -> None:
            self.offset = self.LineInfo.OffsetEnd

            # Move past the newline
            self.Advance(1)

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def SkipWhitespacePrefix(self) -> None:
            offset = self.offset
            line_info = self.LineInfo

            assert offset == line_info.OffsetStart

            delta = line_info.ContentStart - offset
            if delta != 0:
                self.Advance(delta)

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def SkipWhitespaceSuffix(self) -> None:
            offset = self.offset
            line_info = self.LineInfo

            assert offset == line_info.ContentEnd

            delta = line_info.OffsetEnd - offset
            if delta != 0:
                self.Advance(delta)

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def Advance(
            self,
            delta: int,
        ) -> None:
            assert not self.AtEnd()

            offset = self.offset
            line_info = self.LineInfo

            if offset == line_info.OffsetEnd:
                assert delta == 1, delta
                assert self.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine, self.GetNextTokenType()
                self.line_info_index += 1

            else:
                assert offset >= line_info.OffsetStart and offset <= line_info.OffsetEnd, (offset, line_info.OffsetStart, line_info.OffsetEnd)
                assert offset + delta <= line_info.OffsetEnd, (delta, offset, line_info)
                assert (
                    offset >= line_info.ContentStart
                    or (
                        offset == line_info.OffsetStart
                        and (
                            offset + delta == line_info.ContentStart
                            or delta == line_info.OffsetEnd - line_info.OffsetStart
                        )
                    )
                ), (offset, line_info)

            self.offset += delta
