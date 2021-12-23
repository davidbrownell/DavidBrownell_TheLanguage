# ----------------------------------------------------------------------
# |
# |  This file has been automatically generated by PythonVisitor.py.
# |
# ----------------------------------------------------------------------
"""\
BugBug
"""


import copy
from enum import auto, Enum

from CommonEnvironmentEx.Package import InitRelativeImports

with InitRelativeImports():
    from ...CommonLibrary import HashLib_TheLanguage as HashLib
    from ...CommonLibrary.Int_TheLanguage import *
    from ...CommonLibrary.List_TheLanguage import List
    # from ...CommonLibrary.Num_TheLanguage import Num
    # from ...CommonLibrary.Queue_TheLanguage import Queue
    from ...CommonLibrary.Range_TheLanguage import *
    from ...CommonLibrary.Set_TheLanguage import Set
    from ...CommonLibrary.Stack_TheLanguage import Stack
    from ...CommonLibrary.String_TheLanguage import String

    from .Normalize_TheLanguage import LineInfo, NormalizedContent

# Visibility: public
# ClassModifier: mutable
# ClassType: Class
class NormalizedIterator(object):
    """\
    BugBug
    """

    def __init__(self, *args, **kwargs):
        NormalizedIterator._InternalInit(self, list(args), kwargs)

    def _InternalInit(self, args, kwargs):
        # _content, _offset, _line_info_index, _whitespace_range_index, _consumed_dedent_count

        # No bases

        # _content
        if "_content" in kwargs:
            self._content = kwargs.pop("_content")
        elif args:
            self._content = args.pop(0)
        else:
            raise Exception("_content was not provided")

        # _offset
        if "_offset" in kwargs:
            self._offset = kwargs.pop("_offset")
        elif args:
            self._offset = args.pop(0)
        else:
            raise Exception("_offset was not provided")

        # _line_info_index
        if "_line_info_index" in kwargs:
            self._line_info_index = kwargs.pop("_line_info_index")
        elif args:
            self._line_info_index = args.pop(0)
        else:
            raise Exception("_line_info_index was not provided")

        # _whitespace_range_index
        if "_whitespace_range_index" in kwargs:
            self._whitespace_range_index = kwargs.pop("_whitespace_range_index")
        elif args:
            self._whitespace_range_index = args.pop(0)
        else:
            raise Exception("_whitespace_range_index was not provided")

        # _consumed_dedent_count
        if "_consumed_dedent_count" in kwargs:
            self._consumed_dedent_count = kwargs.pop("_consumed_dedent_count")
        elif args:
            self._consumed_dedent_count = args.pop(0)
        else:
            raise Exception("_consumed_dedent_count was not provided")

        self._Init_0b5b153c4edd4245be9a9bf9f3f91781_()

    def __eq__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) == 0

    def __ne__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return True
        return self.__class__.__Compare__(self, other) != 0

    def __lt__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) < 0

    def __le__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) <= 0

    def __gt__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) > 0

    def __ge__(self, other):
        # No bases
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) >= 0

    @classmethod
    def __Compare__(cls, a, b):
        # No bases

        result = cls.__CompareItem__(a._content, b._content)
        if result is not None: return result

        result = cls.__CompareItem__(a._offset, b._offset)
        if result is not None: return result

        result = cls.__CompareItem__(a._line_info_index, b._line_info_index)
        if result is not None: return result

        result = cls.__CompareItem__(a._whitespace_range_index, b._whitespace_range_index)
        if result is not None: return result

        result = cls.__CompareItem__(a._consumed_dedent_count, b._consumed_dedent_count)
        if result is not None: return result

        return 0

    @classmethod
    def __CompareItem__(cls, a, b):
        if a is None and b is None:
            return None

        if a is None: return -1
        if b is None: return 1

        try:
            if a < b: return -1
            if a > b: return 1
        except TypeError:
            a = id(a)
            b = id(b)

            if a < b: return -1
            if a > b: return 1

        return None

    # Visibility: public
    # ClassModifier: immutable
    # ClassType: Enum
    class TokenType(Enum):
        Dedent = 1
        Indent = 2
        WhitespacePrefix = 3
        Content = 4
        WhitespaceSuffix = 5
        EndOfLine = 6
        EndOfFile = 7
        def __eq__(self, other): return self.value == other.value
    LineInfo_WhitespaceRange = LineInfo.WhitespaceRange
    # Return Type: NormalizedIterator
    @staticmethod
    def Create(content, ):
        return NormalizedIterator(NormalizedContentEx.Create(content, ), 0, 0, 0, None, )

    # Return Type: String val
    def _Repr_(self):
        return "[{}, {}] ({})".Format_(self.Line, self.Column, self.Offset, )

    # Return Type: String val
    def ContentProper(self):
        return self._content.content

    # Return Type: PosInt val
    def ContentLengthProper(self):
        return self._content.content_length

    # Return Type: LineInfos val
    def LineInfosProper(self):
        return self._content.line_infos

    # Return Type: HashBytes val
    def HashProper(self):
        return self._content.hash

    # Return Type: Bool val
    def HasEndOfFileDedentsProper(self):
        return self._content.has_end_of_file_dedents

    # Return Type: UIntArch val
    def OffsetProper(self):
        return self._offset

    # Return Type: LineInfo val
    def LineInfoProper(self):
        return self._content.line_infos[self._line_info_index]

    # Return Type: PosInt val
    def LineProper(self):
        return self._line_info_index + 1

    # Return Type: PosInt val
    def ColumnProper(self):
        if self.AtEnd():
            return 1

        return self._offset - self.LineInfoProper().offset_start + 1

    @property
    def Content(self):
        return self.ContentProper()
    @property
    def ContentLength(self):
        return self.ContentLengthProper()
    @property
    def LineInfos(self):
        return self.LineInfosProper()
    @property
    def Hash(self):
        return self.HashProper()
    @property
    def HasEndOfFileDedents(self):
        return self.HasEndOfFileDedentsProper()
    @property
    def Offset(self):
        return self.OffsetProper()
    @property
    def LineInfo(self):
        return self.LineInfoProper()
    @property
    def Line(self):
        return self.LineProper()
    @property
    def Column(self):
        return self.ColumnProper()
    # Return Type: Tuple(HashBytes, UIntArch, UintArch, <UIntArch | None>)
    def ToCacheKey(self):
        return (self.Hash(), self.OffsetProper(), self._whitespace_range_index.Clone(), self._consumed_dedent_count.Clone(), )

    # Return Type: Bool val
    def AtEnd(self):
        line_infos = self.LineInfosProper()
        if self._line_info_index == len(line_infos, ):
            return True

        if (self.HasEndOfFileDedentsProper() and self._line_info_index == len(line_infos, ) - 1 and self._consumed_dedent_count == self.LineInfoProper().num_dedents):
            return True

        return False

    # Return Type: <LineInfo_WhitespaceRange | None> val
    def GetNextWhitespaceRange(self):
        if self.GetNextTokenType() != TokenType.Content:
            return None

        whitespace_ranges = self.LineInfoProper().whitespace_ranges
        whitespace_ranges_length = len(whitespace_ranges)
        if self._whitespace_range_index == whitespace_ranges_length:
            return None

        return whitespace_ranges[self._whitespace_range_index]

    # Return Type: TokenType val
    def GetNextTokenType(self):
        if self.AtEnd():
            return TokenType.EndOfFile

        line_info = self.LineInfoProper()
        if (line_info.num_dedents is not None and self._consumed_dedent_count != line_info.num_dedents):
            return TokenType.Dedent

        if self._offset < line_info.content_start:
            if line_info.new_indentation_value is not None:
                return TokenType.Indent

            return TokenType.WhitespacePrefix

        if self._offset < line_info.content_end:
            return TokenType.Content

        if self._offset >= line_info.content_end and self._offset < line_info.offset_end:
            return TokenType.WhitespaceSuffix

        assert self._offset == line_info.offset_end
        return TokenType.EndOfLine

    # Return Type: Bool val
    def IsBlankLine(self):
        if self.AtEnd():
            return False

        if (self._line_info_index == len(self.LineInfosProper(), ) - 1 and self.HasEndOfFileDedentsProper()):
            return False

        line_info = self.LineInfoProper()
        return line_info.content_end == line_info.content_start

    # Return Type: None
    def ConsumeDedent(self):
        assert self.LineInfoProper().num_dedents is not None
        assert self.OffsetProper() == self.LineInfoProper().offset_start
        if self._consumed_dedent_count is None:
            self._consumed_dedent_count = 0

        self._consumed_dedent_count += 1

    # Return Type: None
    def SkipLine(self):
        self._offset = self.LineInfoProper().offset_end
        self.Advance(1, )

    # Return Type: None
    def SkipWhitespacePrefix(self):
        offset = self._offset
        line_info = self.LineInfoProper()
        assert offset == line_info.offset_start
        delta = line_info.content_start - offset
        if delta != 0:
            self.Advance(delta, )


    # Return Type: None
    def SkipWhitespaceSuffix(self):
        offset = self._offset
        line_info = self.LineInfoProper()
        assert offset == line_info.content_end
        delta = line_info.offset_end - offset
        if delta != 0:
            self.Advance(delta, )


    # Return Type: None
    def Advance(self, delta, ):
        """\
        Advances the offset within a line or moves to a new line if delta == 1.
        """

        offset = self._offset
        line_info = self.LineInfoProper()
        if offset == line_info.offset_end:
            assert delta == 1
            assert self.GetNextTokenType() == TokenType.EndOfLine
            self._line_info_index += 1
            self._whitespace_range_index = 0
            self._consumed_dedent_count = None
        else:
            assert offset >= line_info.offset_start and offset <= line_info.offset_end, "The offset should be within the current line"
            assert offset + delta <= line_info.offset_end, "The delta should not move us past the current line"
            assert (offset >= line_info.content_start or (offset == line_info.offset_start and (offset + delta == line_info.content_start or delta == line_info.offset_end - line_info.offset_start))), "We are looking at content (A), at the beginning of the line and are skipping the whitespace prefix (B) or are skipping the contents on the line (C) <but not the newline itself>"

        self._offset += delta
        if self._offset != self._content.content_length:
            whitespace_ranges = self.LineInfoProper().whitespace_ranges
            whitespace_ranges_len = len(whitespace_ranges)
            while (self._whitespace_range_index < whitespace_ranges_len and self._offset > whitespace_ranges[self._whitespace_range_index].begin):
                self._whitespace_range_index += 1


    # Visibility: private
    # ClassModifier: immutable
    # ClassType: Class
    class NormalizedContentEx(NormalizedContent):
        """\
        Adds end-of-file-dedent info to NormalizedContent
        """

        def __init__(self, *args, **kwargs):
            NormalizedIterator.NormalizedContentEx._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # 

            NormalizedContent._InternalInit(self, args, kwargs)

            # has_end_of_file_dedents
            self.has_end_of_file_dedents = None

            self._Init_4da9b00a3b144e9cb90821a9a0932b5e_()

        def __eq__(self, other):
            if NormalizedContent.__eq__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) == 0

        def __ne__(self, other):
            if NormalizedContent.__ne__(self, other) is False: return False
            if not isinstance(other, self.__class__): return True
            return self.__class__.__Compare__(self, other) != 0

        def __lt__(self, other):
            if NormalizedContent.__lt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) < 0

        def __le__(self, other):
            if NormalizedContent.__le__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) <= 0

        def __gt__(self, other):
            if NormalizedContent.__gt__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) > 0

        def __ge__(self, other):
            if NormalizedContent.__ge__(self, other) is False: return False
            if not isinstance(other, self.__class__): return False
            return self.__class__.__Compare__(self, other) >= 0

        @classmethod
        def __Compare__(cls, a, b):
            result = NormalizedContent.__Compare__(a, b)
            if result != 0: return result

            result = cls.__CompareItem__(a.has_end_of_file_dedents, b.has_end_of_file_dedents)
            if result is not None: return result

            return 0

        @classmethod
        def __CompareItem__(cls, a, b):
            if a is None and b is None:
                return None

            if a is None: return -1
            if b is None: return 1

            try:
                if a < b: return -1
                if a > b: return 1
            except TypeError:
                a = id(a)
                b = id(b)

                if a < b: return -1
                if a > b: return 1

            return None

        # Return Type: NormalizedContentEx val
        @staticmethod
        def Create(content, ):
            return NormalizedContentEx(content.content, content.content_length, content.line_infos, content.hash, )

        # Return Type: None
        def _Init_4da9b00a3b144e9cb90821a9a0932b5e_(self):
            last_line_info = self.line_infos[-1]
            self.has_end_of_file_dedents = (last_line_info.num_dedents is not None and last_line_info.num_dedents > 0 and last_line_info.offset_start == last_line_info.offset_end and last_line_info.content_start == last_line_info.offset_start and last_line_info.content_end == last_line_info.offset_end)

    def Clone(self):
        return self.__class__(self._content, self._offset, self._line_info_index, self._whitespace_range_index, self._consumed_dedent_count)
    # Return Type: None
    def _Init_0b5b153c4edd4245be9a9bf9f3f91781_(self):
        assert self._offset <= self._content.content_length
        if self._offset != self._content.content_length:
            line_info = self._content.line_infos[self._line_info_index]
            assert (self._consumed_dedent_count is None or (line_info.num_dedents is not None and self._consumed_dedent_count <= line_info.num_dedents))


NormalizedContentEx = NormalizedIterator.NormalizedContentEx
TokenType = NormalizedIterator.TokenType
