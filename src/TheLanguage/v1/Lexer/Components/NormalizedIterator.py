# ----------------------------------------------------------------------
# |
# |  NormalizedIterator.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 15:54:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains the NormalizedIterator object"""

import os

from enum import auto, Enum
from typing import List, Optional, Tuple

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment.InstanceCache import InstanceCache, InstanceCacheGet, InstanceCacheReset

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from .Normalize import LineInfo, NormalizedContent, OffsetRange
    from ...Common.Location import Location


# ----------------------------------------------------------------------
def NormalizedIteratorCopyOnWriteDecorator(method):
    # ----------------------------------------------------------------------
    def CopyOnWrite(self, *args, **kwargs):
        if not self._owns_impl:                         # pylint: disable=protected-access
            self._impl = self._impl.Clone()             # pylint: disable=protected-access
            self._owns_impl = True                      # pylint: disable=protected-access

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
            normalized_content.content,
            normalized_content.content_length,
            normalized_content.line_infos,
            normalized_content.hash,
        )

    # ----------------------------------------------------------------------
    def __init__(
        self,
        content: str,
        content_length: int,
        line_infos: List[LineInfo],
        content_hash: bytes,
    ):
        self._impl                          = self.__class__._Impl.Create(
            self.__class__._NormalizedContentEx.Create(
                content,
                content_length,
                line_infos,
                content_hash,
            ),
            0, 0, 0, None,
        )

        self._owns_impl                     = True

    # ----------------------------------------------------------------------
    def Clone(self) -> "NormalizedIterator":
        # Avoid __init__
        obj = self.__class__.__new__(self.__class__)
        super(NormalizedIterator, obj).__init__()

        obj._impl = self._impl
        obj._owns_impl = False

        self._owns_impl = False

        return obj

    # ----------------------------------------------------------------------
    def __eq__(self, other) -> bool:
        if other is None:
            return False

        return self.__class__._Impl.CompareCacheKeys(self.ToCacheKey(), other.ToCacheKey()) == 0

    # ----------------------------------------------------------------------
    def __ne__(self, other) -> bool:
        if other is None:
            return True

        return self.__class__._Impl.CompareCacheKeys(self.ToCacheKey(), other.ToCacheKey()) != 0

    # ----------------------------------------------------------------------
    def __lt__(self, other) -> bool:
        if other is None:
            return False

        return self.__class__._Impl.CompareCacheKeys(self.ToCacheKey(), other.ToCacheKey()) < 0

    # ----------------------------------------------------------------------
    def __le__(self, other) -> bool:
        if other is None:
            return False

        return self.__class__._Impl.CompareCacheKeys(self.ToCacheKey(), other.ToCacheKey()) <= 0

    # ----------------------------------------------------------------------
    def __gt__(self, other) -> bool:
        if other is None:
            return True

        return self.__class__._Impl.CompareCacheKeys(self.ToCacheKey(), other.ToCacheKey()) > 0

    # ----------------------------------------------------------------------
    def __ge__(self, other) -> bool:
        if other is None:
            return True

        return self.__class__._Impl.CompareCacheKeys(self.ToCacheKey(), other.ToCacheKey()) >= 0

    # ----------------------------------------------------------------------
    def __repr__(self) -> str:
        return self._impl.Repr()

    # ----------------------------------------------------------------------
    def __getattr__(self, attr):
        return getattr(self._impl, attr)

    # ----------------------------------------------------------------------
    @property
    def content(self) -> str:
        return self._impl.content.content

    @property
    def content_length(self) -> int:
        return self._impl.content.content_length

    @property
    def line_infos(self) -> List[LineInfo]:
        return self._impl.content.line_infos

    @property
    def has_end_of_file_dedents(self) -> bool:
        return self._impl.content.has_end_of_file_dedents

    # ----------------------------------------------------------------------
    def ToLocation(self) -> Location:
        return Location.Create(self.line, self.column)

    # ----------------------------------------------------------------------
    @NormalizedIteratorCopyOnWriteDecorator
    def ConsumeDedent(self) -> "NormalizedIterator":
        self._impl.ConsumeDedent()
        return self

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
    class _NormalizedContentEx(object):
        content: str
        content_length: int
        line_infos: List[LineInfo]
        hash: bytes
        has_end_of_file_dedents: bool       = field(init=False)

        # ----------------------------------------------------------------------
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            object.__setattr__(
                self,
                "has_end_of_file_dedents",
                (
                    bool(self.line_infos)
                    and self.line_infos[-1].num_dedents is not None
                    and self.line_infos[-1].num_dedents > 0
                    and self.line_infos[-1].offset_begin == self.line_infos[-1].offset_end
                    and self.line_infos[-1].content_begin == self.line_infos[-1].offset_end
                    and self.line_infos[-1].content_end == self.line_infos[-1].offset_end
                ),
            )

    # ----------------------------------------------------------------------
    @dataclass
    class _Impl(InstanceCache):
        """Implementation that can be shared by multiple NormalizedIterator when values have not changed"""

        content: "NormalizedIterator._NormalizedContentEx"

        line_info_index: int
        offset: int

        whitespace_range_index: int
        consumed_dedent_count: Optional[int]

        # ----------------------------------------------------------------------
        @classmethod
        def Create(cls, *args, **kwargs):
            """\
            This hack avoids pylint warnings associated with invoking dynamically
            generated constructors with too many methods.
            """
            return cls(*args, **kwargs)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            InstanceCache.__init__(self)

        # ----------------------------------------------------------------------
        @property
        def line_info(self) -> LineInfo:
            return self.content.line_infos[self.line_info_index]

        @property
        def line(self) -> int:
            return self.line_info_index + 1

        @property
        def column(self) -> int:
            if self.AtEnd():
                return 1

            return self.offset - self.line_info.offset_begin + 1

        # ----------------------------------------------------------------------
        def Clone(self):
            return self.__class__(
                self.content,
                self.line_info_index,
                self.offset,
                self.whitespace_range_index,
                self.consumed_dedent_count,
            )

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def AtEnd(self) -> bool:
            if self.line_info_index == len(self.content.line_infos):
                return True

            if (
                self.content.has_end_of_file_dedents
                and self.line_info_index == len(self.content.line_infos) - 1
                and self.consumed_dedent_count == self.content.line_infos[-1].num_dedents
            ):
                return True

            return False

        # ----------------------------------------------------------------------
        CacheKeyType                        = Tuple[
            bytes,
            int,
            Optional[int],
        ]

        @InstanceCacheGet
        def ToCacheKey(self) -> CacheKeyType:
            return (
                self.content.hash,
                self.offset,
                self.consumed_dedent_count,
            )

        # ----------------------------------------------------------------------
        @staticmethod
        def CompareCacheKeys(
            this_key: CacheKeyType,
            that_key: CacheKeyType,
        ) -> int:
            # hash
            if this_key[0] < that_key[0]:
                return -1
            if this_key[0] > that_key[0]:
                return 1

            # offset
            if this_key[1] < that_key[1]:
                return -1
            if this_key[1] > that_key[1]:
                return 1

            # consumed_dedent_count
            this_value = this_key[2]
            that_value = that_key[2]

            if this_value is None and that_value is None:
                pass
            elif this_value is None:
                return -1
            elif that_value is None:
                return 1
            elif this_value < that_value:
                return -1
            elif this_value > that_value:
                return 1

            return 0

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def Repr(self) -> str:
            return "[{}, {}] ({})".format(self.line, self.column, self.offset)

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def GetNextTokenType(self) -> "NormalizedIterator.TokenType":
            if self.AtEnd():
                return NormalizedIterator.TokenType.EndOfFile

            line_info = self.line_info

            if (
                line_info.num_dedents is not None
                and self.consumed_dedent_count != line_info.num_dedents
            ):
                return NormalizedIterator.TokenType.Dedent

            if self.offset < line_info.content_begin:
                if line_info.new_indent_value is not None:
                    return NormalizedIterator.TokenType.Indent

                return NormalizedIterator.TokenType.WhitespacePrefix

            if self.offset < line_info.content_end:
                return NormalizedIterator.TokenType.Content

            if self.offset >= line_info.content_end and self.offset < line_info.offset_end:
                return NormalizedIterator.TokenType.WhitespaceSuffix

            assert self.offset == line_info.offset_end
            return NormalizedIterator.TokenType.EndOfLine

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def GetNextWhitespaceRange(self) -> Optional[OffsetRange]:
            if self.GetNextTokenType() != NormalizedIterator.TokenType.Content:
                return None

            whitespace_ranges = self.line_info.whitespace_ranges

            if not whitespace_ranges or self.whitespace_range_index == len(whitespace_ranges):
                return None

            return whitespace_ranges[self.whitespace_range_index]

        # ----------------------------------------------------------------------
        @InstanceCacheGet
        def IsBlankLine(self) -> bool:
            """Returns True if the offset is positioned at the beginning of a blank line"""

            # We don't have a line when we are at the end, so it can't be a blank line by definition
            if self.AtEnd():
                return False

            # The trailing dedent lines should not be considered blank lines
            if (
                self.line_info_index == len(self.content.line_infos) - 1
                and self.content.has_end_of_file_dedents
            ):
                return False

            line_info = self.line_info
            return line_info.content_end == line_info.content_begin

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def ConsumeDedent(self) -> None:
            assert self.line_info.num_dedents is not None
            assert self.offset == self.line_info.offset_begin

            if self.consumed_dedent_count is None:
                self.consumed_dedent_count = 0
            else:
                assert self.consumed_dedent_count is not None

            self.consumed_dedent_count += 1

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def SkipLine(self) -> None:
            self.offset = self.line_info.offset_end

            # Move past the newline
            self._AdvanceImpl(1)

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def SkipWhitespacePrefix(self) -> None:
            offset = self.offset
            line_info = self.line_info

            assert offset == line_info.offset_begin

            delta = line_info.content_begin - offset
            if delta != 0:
                self._AdvanceImpl(delta)

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def SkipWhitespaceSuffix(self) -> None:
            offset = self.offset
            line_info = self.line_info

            assert offset == line_info.content_end

            delta = line_info.offset_end - offset
            if delta != 0:
                self._AdvanceImpl(delta)

        # ----------------------------------------------------------------------
        @InstanceCacheReset
        def Advance(
            self,
            delta: int,
        ) -> None:
            return self._AdvanceImpl(delta)

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        def _AdvanceImpl(
            self,
            delta: int,
        ) -> None:
            # Only invoke this method from methods that have reset the cache!
            assert not self.AtEnd()

            offset = self.offset
            line_info = self.line_info

            if offset == line_info.offset_end:
                assert delta == 1, delta
                assert self.GetNextTokenType() == NormalizedIterator.TokenType.EndOfLine, self.GetNextTokenType()

                self.line_info_index += 1

                self.whitespace_range_index = 0
                self.consumed_dedent_count = None

            else:
                assert offset >= line_info.offset_begin and offset <= line_info.offset_end, (offset, line_info.offset_begin, line_info.offset_end)
                assert offset + delta <= line_info.offset_end, (delta, offset, line_info)
                assert (
                    offset >= line_info.content_begin
                    or (
                        offset == line_info.offset_begin
                        and (
                            offset + delta == line_info.content_begin
                            or delta == line_info.offset_end - line_info.offset_begin
                        )
                    )
                ), (offset, line_info)

            self.offset += delta

            # Determine if applying the delta indicates that we are looking at a new whitespace range.
            if self.offset != self.content.content_length:
                whitespace_ranges = self.line_info.whitespace_ranges

                while (
                    self.whitespace_range_index < len(whitespace_ranges)
                    and self.offset > whitespace_ranges[self.whitespace_range_index].begin
                ):
                    self.whitespace_range_index += 1
