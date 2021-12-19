# ----------------------------------------------------------------------
# |
# |  This file has been automatically generated by PythonVisitor.py.
# |
# ----------------------------------------------------------------------
"""\
Contains types and functions used to normalize source content prior to lexing. This code works very
hard to remain agnostic to the syntax/grammar that ultimately relies on the normalized content.
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

    from ..Error_TheLanguage import Error

# Visibility: public
# ClassModifier: immutable
# ClassType: Exception
class InvalidTabsAndSpacesError(Error):
    def __init__(self, *args, **kwargs):
        InvalidTabsAndSpacesError._InternalInit(self, list(args), kwargs)

    def _InternalInit(self, args, kwargs):
        # 

        Error._InternalInit(self, args, kwargs)

        # No members

        self._Init_603b63f4d74c4474bc9a62bfa38a4fa5_()

    def __eq__(self, other):
        if Error.__eq__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) == 0

    def __ne__(self, other):
        if Error.__ne__(self, other) is False: return False
        if not isinstance(other, self.__class__): return True
        return self.__class__.__Compare__(self, other) != 0

    def __lt__(self, other):
        if Error.__lt__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) < 0

    def __le__(self, other):
        if Error.__le__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) <= 0

    def __gt__(self, other):
        if Error.__gt__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) > 0

    def __ge__(self, other):
        if Error.__ge__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) >= 0

    @classmethod
    def __Compare__(cls, a, b):


        return 0

    def _Init_603b63f4d74c4474bc9a62bfa38a4fa5_(self):
        pass

    # Return Type: String
    def _GetMessageTemplate(self):
        return "The spaces and/or tabs used to indent this line differ from the spaces and/or table used on previous lines."

# Visibility: public
# ClassModifier: immutable
# ClassType: Exception
class NoClosingMultilineTokenError(Error):
    def __init__(self, *args, **kwargs):
        NoClosingMultilineTokenError._InternalInit(self, list(args), kwargs)

    def _InternalInit(self, args, kwargs):
        # 

        Error._InternalInit(self, args, kwargs)

        # No members

        self._Init_633e30a89968434ba246206bd745cefc_()

    def __eq__(self, other):
        if Error.__eq__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) == 0

    def __ne__(self, other):
        if Error.__ne__(self, other) is False: return False
        if not isinstance(other, self.__class__): return True
        return self.__class__.__Compare__(self, other) != 0

    def __lt__(self, other):
        if Error.__lt__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) < 0

    def __le__(self, other):
        if Error.__le__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) <= 0

    def __gt__(self, other):
        if Error.__gt__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) > 0

    def __ge__(self, other):
        if Error.__ge__(self, other) is False: return False
        if not isinstance(other, self.__class__): return False
        return self.__class__.__Compare__(self, other) >= 0

    @classmethod
    def __Compare__(cls, a, b):


        return 0

    def _Init_633e30a89968434ba246206bd745cefc_(self):
        pass

    # Return Type: String
    def _GetMessageTemplate(self):
        return "A closing token was not found to match this multi-line opening token."

# Visibility: protected
# ClassModifier: immutable
# ClassType: Class
class LineInfo(object):
    def __init__(self, *args, **kwargs):
        LineInfo._InternalInit(self, list(args), kwargs)

    def _InternalInit(self, args, kwargs):
        # offset_start, offset_end, content_start, content_end, whitespace_ranges, num_dedents=None, new_indentation_value=None

        # No bases

        # offset_start
        if "offset_start" in kwargs:
            self.offset_start = kwargs.pop("offset_start")
        elif args:
            self.offset_start = args.pop(0)
        else:
            raise Exception("offset_start was not provided")

        # offset_end
        if "offset_end" in kwargs:
            self.offset_end = kwargs.pop("offset_end")
        elif args:
            self.offset_end = args.pop(0)
        else:
            raise Exception("offset_end was not provided")

        # content_start
        if "content_start" in kwargs:
            self.content_start = kwargs.pop("content_start")
        elif args:
            self.content_start = args.pop(0)
        else:
            raise Exception("content_start was not provided")

        # content_end
        if "content_end" in kwargs:
            self.content_end = kwargs.pop("content_end")
        elif args:
            self.content_end = args.pop(0)
        else:
            raise Exception("content_end was not provided")

        # whitespace_ranges
        if "whitespace_ranges" in kwargs:
            self.whitespace_ranges = kwargs.pop("whitespace_ranges")
        elif args:
            self.whitespace_ranges = args.pop(0)
        else:
            raise Exception("whitespace_ranges was not provided")

        # num_dedents
        if "num_dedents" in kwargs:
            self.num_dedents = kwargs.pop("num_dedents")
        elif args:
            self.num_dedents = args.pop(0)
        else:
            self.num_dedents = None

        # new_indentation_value
        if "new_indentation_value" in kwargs:
            self.new_indentation_value = kwargs.pop("new_indentation_value")
        elif args:
            self.new_indentation_value = args.pop(0)
        else:
            self.new_indentation_value = None

        self._Init_d8ae241a8d5349bb8e948e7f975d1b02_()

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
        if a.offset_start is None and b.offset_start is None: pass
        elif a.offset_start is None: return -1
        elif b.offset_start is None: return 1
        elif a.offset_start < b.offset_start: return -1
        elif a.offset_start > b.offset_start: return 1

        if a.offset_end is None and b.offset_end is None: pass
        elif a.offset_end is None: return -1
        elif b.offset_end is None: return 1
        elif a.offset_end < b.offset_end: return -1
        elif a.offset_end > b.offset_end: return 1

        if a.content_start is None and b.content_start is None: pass
        elif a.content_start is None: return -1
        elif b.content_start is None: return 1
        elif a.content_start < b.content_start: return -1
        elif a.content_start > b.content_start: return 1

        if a.content_end is None and b.content_end is None: pass
        elif a.content_end is None: return -1
        elif b.content_end is None: return 1
        elif a.content_end < b.content_end: return -1
        elif a.content_end > b.content_end: return 1

        if a.whitespace_ranges is None and b.whitespace_ranges is None: pass
        elif a.whitespace_ranges is None: return -1
        elif b.whitespace_ranges is None: return 1
        elif a.whitespace_ranges < b.whitespace_ranges: return -1
        elif a.whitespace_ranges > b.whitespace_ranges: return 1

        if a.num_dedents is None and b.num_dedents is None: pass
        elif a.num_dedents is None: return -1
        elif b.num_dedents is None: return 1
        elif a.num_dedents < b.num_dedents: return -1
        elif a.num_dedents > b.num_dedents: return 1

        if a.new_indentation_value is None and b.new_indentation_value is None: pass
        elif a.new_indentation_value is None: return -1
        elif b.new_indentation_value is None: return 1
        elif a.new_indentation_value < b.new_indentation_value: return -1
        elif a.new_indentation_value > b.new_indentation_value: return 1

        return 0

    # Visibility: public
    # ClassModifier: immutable
    # ClassType: Class
    class WhitespaceRange(object):
        def __init__(self, *args, **kwargs):
            LineInfo.WhitespaceRange._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # begin, end

            # No bases

            # begin
            if "begin" in kwargs:
                self.begin = kwargs.pop("begin")
            elif args:
                self.begin = args.pop(0)
            else:
                raise Exception("begin was not provided")

            # end
            if "end" in kwargs:
                self.end = kwargs.pop("end")
            elif args:
                self.end = args.pop(0)
            else:
                raise Exception("end was not provided")

            self._Init_1c59bd161a2747febf4e89c35e5b371e_()

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
            if a.begin is None and b.begin is None: pass
            elif a.begin is None: return -1
            elif b.begin is None: return 1
            elif a.begin < b.begin: return -1
            elif a.begin > b.begin: return 1

            if a.end is None and b.end is None: pass
            elif a.end is None: return -1
            elif b.end is None: return 1
            elif a.end < b.end: return -1
            elif a.end > b.end: return 1

            return 0

        # Return Type: None
        def _Init_1c59bd161a2747febf4e89c35e5b371e_(self):
            assert self.begin < self.end

    # Type alias: public WhitespaceRanges = List<WhitespaceRange, >{min_length'=0, }
    # Return Type: Bool
    def HasWhitespacePrefix(self):
        return self.content_start != self.offset_start

    # Return Type: Bool
    def HasContent(self):
        return self.content_start != self.content_end

    # Return Type: Bool
    def HasWhitespaceSuffix(self):
        return self.content_end != self.offset_end

    # Return Type: None
    def _Init_d8ae241a8d5349bb8e948e7f975d1b02_(self):
        assert self.offset_end >= self.offset_start
        assert self.content_start >= self.offset_start
        assert self.content_end >= self.content_start
        assert self.content_end <= self.offset_end

    @property
    def OffsetStart(self): return self.offset_start
    @property
    def OffsetEnd(self): return self.offset_end
    @property
    def ContentStart(self): return self.content_start
    @property
    def ContentEnd(self): return self.content_end
    @property
    def NumDedents(self): return self.num_dedents
    @property
    def NewIndentationValue(self): return self.new_indentation_value
# Visibility: public
# ClassModifier: immutable
# ClassType: Class
class NormalizedContent(object):
    def __init__(self, *args, **kwargs):
        NormalizedContent._InternalInit(self, list(args), kwargs)

    def _InternalInit(self, args, kwargs):
        # content, content_length, line_infos, hash

        # No bases

        # content
        if "content" in kwargs:
            self.content = kwargs.pop("content")
        elif args:
            self.content = args.pop(0)
        else:
            raise Exception("content was not provided")

        # content_length
        if "content_length" in kwargs:
            self.content_length = kwargs.pop("content_length")
        elif args:
            self.content_length = args.pop(0)
        else:
            raise Exception("content_length was not provided")

        # line_infos
        if "line_infos" in kwargs:
            self.line_infos = kwargs.pop("line_infos")
        elif args:
            self.line_infos = args.pop(0)
        else:
            raise Exception("line_infos was not provided")

        # hash
        if "hash" in kwargs:
            self.hash = kwargs.pop("hash")
        elif args:
            self.hash = args.pop(0)
        else:
            raise Exception("hash was not provided")

        self._Init_94b9be41ef6e48dd9e9709d29829beb7_()

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
        if a.content is None and b.content is None: pass
        elif a.content is None: return -1
        elif b.content is None: return 1
        elif a.content < b.content: return -1
        elif a.content > b.content: return 1

        if a.content_length is None and b.content_length is None: pass
        elif a.content_length is None: return -1
        elif b.content_length is None: return 1
        elif a.content_length < b.content_length: return -1
        elif a.content_length > b.content_length: return 1

        if a.line_infos is None and b.line_infos is None: pass
        elif a.line_infos is None: return -1
        elif b.line_infos is None: return 1
        elif a.line_infos < b.line_infos: return -1
        elif a.line_infos > b.line_infos: return 1

        if a.hash is None and b.hash is None: pass
        elif a.hash is None: return -1
        elif b.hash is None: return 1
        elif a.hash < b.hash: return -1
        elif a.hash > b.hash: return 1

        return 0

    def _Init_94b9be41ef6e48dd9e9709d29829beb7_(self):
        pass

    # Type alias: public LineInfos = List<LineInfo, >{min_length'=1, }
    # Type alias: public HashBytes = List<Int8, >{min_length'=32, max_length'=32, }
    # Return Type: NormalizedContent
    @staticmethod
    def Create(content, content_length, line_infos, ):
        hasher = HashLib.Sha256()
        hasher.Update(content, )
        hash = hasher.Digest()
        return NormalizedContent(content, content_length, line_infos, hash, )

    @property
    def Content(self): return self.content
    @property
    def ContentLen(self): return self.content_length
    @property
    def ContentLength(self): return self.content_length
    @property
    def LineInfos(self): return self.line_infos
    @property
    def Hash(self): return self.hash
# Return Type: NormalizedContent
def Normalize_(content, multiline_tokens_to_ignore=None, suppress_indentation_func=None, ):
    """\
    Normalizes the provided content by organizing it into lines that have knowledge of their indentation
    relative to the lines around them.
    """

    content = (content if content and content[-1] == '\n' else (content + '\n')) # as val
    multiline_tokens_to_ignore = (multiline_tokens_to_ignore or Set()) # as val
    suppress_indentation_func = (suppress_indentation_func or ((lambda offset_start, offset_end, content_start, content_end, : False))) # as val
    content_length = len(content)
    # Visibility: private
    # ClassModifier: immutable
    # ClassType: Class
    class IndentationInfo(object):
        def __init__(self, *args, **kwargs):
            IndentationInfo._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # num_chars, value

            # No bases

            # num_chars
            if "num_chars" in kwargs:
                self.num_chars = kwargs.pop("num_chars")
            elif args:
                self.num_chars = args.pop(0)
            else:
                raise Exception("num_chars was not provided")

            # value
            if "value" in kwargs:
                self.value = kwargs.pop("value")
            elif args:
                self.value = args.pop(0)
            else:
                raise Exception("value was not provided")

            self._Init_b036d95dc9d64bf2a6304b259f03fdd3_()

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
            if a.num_chars is None and b.num_chars is None: pass
            elif a.num_chars is None: return -1
            elif b.num_chars is None: return 1
            elif a.num_chars < b.num_chars: return -1
            elif a.num_chars > b.num_chars: return 1

            if a.value is None and b.value is None: pass
            elif a.value is None: return -1
            elif b.value is None: return 1
            elif a.value < b.value: return -1
            elif a.value > b.value: return 1

            return 0

        def _Init_b036d95dc9d64bf2a6304b259f03fdd3_(self):
            pass

    # Visibility: private
    # ClassModifier: immutable
    # ClassType: Class
    class MultilineTokenInfo(object):
        def __init__(self, *args, **kwargs):
            MultilineTokenInfo._InternalInit(self, list(args), kwargs)

        def _InternalInit(self, args, kwargs):
            # line_index, num_delimiters

            # No bases

            # line_index
            if "line_index" in kwargs:
                self.line_index = kwargs.pop("line_index")
            elif args:
                self.line_index = args.pop(0)
            else:
                raise Exception("line_index was not provided")

            # num_delimiters
            if "num_delimiters" in kwargs:
                self.num_delimiters = kwargs.pop("num_delimiters")
            elif args:
                self.num_delimiters = args.pop(0)
            else:
                raise Exception("num_delimiters was not provided")

            self._Init_a3e7afcf4a5145df9c836134e6c94950_()

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
            if a.line_index is None and b.line_index is None: pass
            elif a.line_index is None: return -1
            elif b.line_index is None: return 1
            elif a.line_index < b.line_index: return -1
            elif a.line_index > b.line_index: return 1

            if a.num_delimiters is None and b.num_delimiters is None: pass
            elif a.num_delimiters is None: return -1
            elif b.num_delimiters is None: return 1
            elif a.num_delimiters < b.num_delimiters: return -1
            elif a.num_delimiters > b.num_delimiters: return 1

            return 0

        def _Init_a3e7afcf4a5145df9c836134e6c94950_(self):
            pass

    line_infos = List()
    indentation_stack = Stack.Create(IndentationInfo(0, 0, ), )
    multiline_token_info = None # as <MultilineTokenInfo | None>
    offset = 0 # as IntArch
    # Return Type: LineInfo
    def CreateLineInfo():
        nonlocal offset
        nonlocal indentation_stack

        offset_start = offset
        whitespace_ranges = List()
        whitespace_start = None # as <TypeOf(offset) | None>
        while True:
            char = content[offset]
            if char == ' ' or char == '\t':
                if whitespace_start is None:
                    whitespace_start = offset

            else:
                if whitespace_start is not None:
                    whitespace_ranges.InsertBack_(LineInfo.WhitespaceRange(whitespace_start, offset, ), )
                    whitespace_start = None

                if char == '\n':
                    break


            offset += 1
        offset_end = offset
        content_start = None
        content_end = None
        if not whitespace_ranges:
            content_start = offset_start
            content_end = offset_end
        else:
            # Scoped Statement: Begin
            initial_range = whitespace_ranges.Peek_(0, )

            if initial_range.begin == offset_start:
                content_start = initial_range.end
            else:
                content_start = offset_start

            # Scoped Statement: End

            # Scoped Statement: Begin
            last_range = whitespace_ranges.Peek_(-1, )

            if last_range.end == offset_end and last_range.begin != offset_start:
                content_end = last_range.begin
            else:
                content_end = offset_end

            # Scoped Statement: End


        num_dedents = None
        new_indentation_value = None
        if (content_start == content_end or multiline_token_info is not None or suppress_indentation_func(offset_start, offset_end, content_start, content_end, )):
            num_dedents = None
            new_indentation_value = None
        else:
            this_num_chars = content_start - offset_start
            this_indentation_value = 0
            if this_num_chars != 0:
                for index in IntGenerator(offset_start, content_start, ):
                    char = content[index]
                    if char == ' ':
                        this_indentation_value += 1
                    elif char == '\t':
                        this_indentation_value += (index - offset_start + 1) * 100
                    else:
                        assert False, char


            if (this_num_chars == indentation_stack.Peek().num_chars and this_indentation_value != indentation_stack.Peek().value):
                raise InvalidTabsAndSpacesError(len(line_infos) + 1, content_start - offset_start + 1, )

            num_dedents = 0
            while this_num_chars < indentation_stack.Peek().num_chars:
                indentation_stack.Pop_()
                num_dedents += 1
            if num_dedents == 0:
                num_dedents = None

            if this_num_chars > indentation_stack.Peek().num_chars:
                new_indentation_value = this_indentation_value
                indentation_stack.Push_(IndentationInfo(this_num_chars, this_indentation_value, ), )
            else:
                new_indentation_value = None


        offset += 1
        return LineInfo(offset_start, offset_end, content_start, content_end, whitespace_ranges, num_dedents, new_indentation_value, )

    while offset < content_length:
        line_infos.Append_(CreateLineInfo(), )
        num_multiline_delimiters = GetNumMultilineTokenDelimiters(content, start_index=line_infos[-1].content_start, end_index=line_infos[-1].content_end, )
        if (num_multiline_delimiters != 0 and content[line_infos[-1].content_start:line_infos[-1].content_end] not in multiline_tokens_to_ignore):
            if multiline_token_info is None:
                multiline_token_info = MultilineTokenInfo(len(line_infos) - 1, num_multiline_delimiters, )
            else:
                multiline_token_info = None


    if multiline_token_info is not None:
        line_info = line_infos[multiline_token_info.line_index]
        raise NoClosingMultilineTokenError(multiline_token_info.line_index + 1, line_info.content_start - line_info.offset_start + 1, )

    if len(indentation_stack) > 1:
        line_infos.append(LineInfo(offset, offset, offset, offset, List(), len(indentation_stack) - 1, None, ), )

    return NormalizedContent.Create(content, content_length, line_infos, )

multiline_token_delimiter_length = 3
import textwrap
MultilineTokenDelimiterRegexTemplate        = textwrap.dedent(
    r"""{{header}}(?#
        Don't consume other triplets.
            The number of items here must match
            MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH.           )(?!{triplet_item}{triplet_item}{triplet_item})(?#
        Value                                           )(?P<value>.*?)(?#
        No slash as a prefix to the closing triplet[s]  )(?<!\\)(?#
    ){{footer}}""",
).format(
    triplet_item=r"[^A-Za-z0-9 \t\n]",
)
# Return Type: UInt
def GetNumMultilineTokenDelimiters(content, start_index, end_index, ):
    """\
    Returns the number of valid multiline token delimiter items at the given position in the provided content.
    See the comments in `Normalize` for more information.
    """

    if start_index == end_index:
        return 0

    if (end_index - start_index) % multiline_token_delimiter_length != 0:
        return 0

    index = start_index
    while index != end_index:
        char = content[index]
        if ((char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z') or (char >= '0' and char <= '9') or char == '_'):
            return 0

        for offset in IntGenerator(index + 1, index + multiline_token_delimiter_length, ):
            if content[offset] != char:
                return 0

        index += multiline_token_delimiter_length
    return (end_index - start_index) // multiline_token_delimiter_length

