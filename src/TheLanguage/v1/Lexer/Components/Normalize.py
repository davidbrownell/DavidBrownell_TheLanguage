# ----------------------------------------------------------------------
# |
# |  Normalize.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-04-01 14:57:15
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types and functions used to normalize source content for lexing"""

import hashlib
import os
import textwrap

from typing import Callable, List, Optional, Set

from dataclasses import dataclass, field, InitVar

import CommonEnvironment
from CommonEnvironment.YamlRepr import ObjectReprImplBase

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

with InitRelativeImports():
    from ..Error import CreateError, Location


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
InvalidTabsAndSpacesError                   = CreateError(
    "The spaces and/or tabs used to indent this line differ from the spaces and/or tabs used on previous lines",
)

NoClosingMultilineTokenError                = CreateError(
    "A closing token was not found to match this mutli-line opening token",
)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class OffsetRange(ObjectReprImplBase):
    begin: int
    end: int

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
        assert self.begin >= 0
        assert self.begin < self.end

        ObjectReprImplBase.__init__(self)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class LineInfo(ObjectReprImplBase):
    """Information about a single line"""

    offset_begin: int
    offset_end: int

    content_begin: int
    content_end: int

    whitespace_ranges: List[OffsetRange]

    num_dedents: Optional[int]              = field(default=None)
    new_indent_value: Optional[int]         = field(default=None)

    has_whitespace_prefix: bool             = field(init=False)
    has_content: bool                       = field(init=False)
    has_whitespace_suffix: bool             = field(init=False)

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
        ObjectReprImplBase.__init__(self)

        assert self.offset_begin >= 0
        assert self.offset_end >= self.offset_begin
        assert self.content_begin >= self.offset_begin
        assert self.content_end >= self.content_begin
        assert self.content_end <= self.offset_end
        assert self.num_dedents is None or self.num_dedents > 0
        assert self.new_indent_value is None or self.new_indent_value > 0

        object.__setattr__(self, "has_whitespace_prefix", self.content_begin != self.offset_begin)
        object.__setattr__(self, "has_content", self.content_begin != self.content_end)
        object.__setattr__(self, "has_whitespace_suffix", self.content_end != self.offset_end)


# ----------------------------------------------------------------------
@dataclass(frozen=True, repr=False)
class NormalizedContent(ObjectReprImplBase):
    content: str
    content_length: int
    line_infos: List[LineInfo]

    hash_param: InitVar[Optional[bytes]]
    hash: bytes                             = field(init=False)

    # ----------------------------------------------------------------------
    @classmethod
    def Create(cls, *args, **kwargs):
        """\
        This hack avoids pylint warnings associated with invoking dynamically
        generated constructors with too many methods.
        """
        return cls(*args, **kwargs)

    # ----------------------------------------------------------------------
    def __post_init__(self, hash_param):
        ObjectReprImplBase.__init__(
            self,
            content=None,
            line_infos=None,
            hash=None,
        )

        assert self.content
        assert self.content_length
        assert self.line_infos

        if hash_param is None:
            hash_param = self.__class__.CalculateHash(self.content)

        object.__setattr__(self, "hash", hash_param)

    # ----------------------------------------------------------------------
    @staticmethod
    def CalculateHash(
        content: str,
    ) -> bytes:
        hasher = hashlib.sha256()
        hasher.update(content.encode("utf-8"))
        return hasher.digest()


# ----------------------------------------------------------------------
# Note that this regular expression template needs to change any time that there is a change
# with `multiline_token_delimiter_length` or `GetNumMultilineTokenDelimiters`.
# ----------------------------------------------------------------------
multiline_token_delimiter_length            = 3

MultilineTokenDelimiterRegexTemplate        = textwrap.dedent(
    r"""{{header}}(?#
        Don't consume other triplets.
            The number of items here must match
            multiline_token_delimiter_length.           )(?!{triplet_item}{triplet_item}{triplet_item})(?#
        Value                                           )(?P<value>.*?)(?#
        No slash as a prefix to the closing triplet[s]  )(?<!\\)(?#
    ){{footer}}""",
).format(
    triplet_item=r"[^A-Za-z0-9 \t\n]",
)


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def GetNumMultilineTokenDelimiters(
    content: str,
    begin_index: int=0,
    end_index: Optional[int]=None,
) -> int:
    """\
    Returns the number of valid multiline token items at the given position in the provided content.

    See comments in `Normalize` for more information.
    """

    if end_index is None:
        end_index = len(content)

    if begin_index == end_index:
        return 0

    if (end_index - begin_index) % multiline_token_delimiter_length != 0:
        return 0

    index = begin_index

    while index != end_index:
        # The character must be a symbol
        if content[index].isalnum():
            return 0

        # Every items within the delimiter must be the same
        for offset in range(index + 1, index + multiline_token_delimiter_length):
            if content[offset] != content[index]:
                return 0

        index += multiline_token_delimiter_length

    return (end_index - begin_index) // multiline_token_delimiter_length


# ----------------------------------------------------------------------
def Normalize(
    content: str,

    # A set of tokens that look and feel like multi-line toggle tokens, but should not be considered
    # as such. An example of when to use this would be "---" when parsing yaml files.
    multiline_tokens_to_ignore: Optional[Set[str]]=None,

    # Optional function that can be used to suppress the generation of indentation infomration
    # on a per-line basis. An example of when to use this would be when a line starts with a comment
    # that isn't aligned when the current indentation level.
    suppress_indentation_func: Optional[
        Callable[
            [
                int,                        # offset_begin
                int,                        # offset_end
                int,                        # content_begin
                int                         # content_end
            ],
            bool                            # True to suppress the indentation change, False to allow it
        ]
    ]=None,
) -> NormalizedContent:
    """Normalizes the provided content to prevent repeated calculations"""

    # This code is intended to be a general purpose normalization algorithm, with no special
    # knowledge of underling grammars. In most cases, it is fairly straight forward to maintain
    # this architectural distinction. However, multi-line phrases present a problem.
    #
    # We track indentation change for each line, but multi-line phrases are special in that
    # any indentation changes that happen within that phrase should not impact the subsequent
    # phrases.
    #
    # Consider this python content:
    #
    #                                         Indentation Level   Indentation Stack
    #                                         -----------------   -----------------
    #     if True:                          #         0           [0]
    #         print(                        #         4           [0, 4]
    #             textwrap.dedent(          #         8           [0, 4, 8]
    #                 """\                  #        12           [0, 4, 8, 12]
    #                 Proper indentation.   #        12           [0, 4, 8, 12]
    #               Wonky indentation.      #        10           [0, 4, 8, 10]
    #                 Normal indentation.   #        12           [0, 4, 8, 10, 12]
    #                 """,                  #        12           [0, 4, 8, 10, 12]
    #             ),                        #         8           [0, 4, 8]             !!! Note that 2 dedents were introduced, rather than the 1 that was expected
    #         )                             #         4           [0, 4]
    #                                       #         0           [0]
    #
    # Since indents and dedents are meaningful, this presents a problem. To work around this, we
    # introduce the opt-in concept that (some/most?) multi-line phrases should not make changes
    # to the indentation stack. With this in place, the example above becomes:
    #
    #                                         Indentation Level   Indentation Stack
    #                                         -----------------   -----------------
    #     if True:                          #         0           [0]
    #         print(                        #         4           [0, 4]
    #             textwrap.dedent(          #         8           [0, 4, 8]
    #                 """\                  #        12           [0, 4, 8, 12]
    #                 Proper indentation.   #        12           ????
    #               Wonky indentation.      #        10           ????
    #                 Normal indentation.   #        12           ????
    #                 """,                  #        12           [0, 4, 8, 12]
    #             ),                        #         8           [0, 4, 8]             !!! Note that the indentation stack is the same existing the multi-line phrase as it was entering it
    #         )                             #         4           [0, 4]
    #                                       #         0           [0]
    #
    # However, this presents a new challenge - how do we recognize multi-line phrases without
    # any knowledge of the underlying grammar? We could hard-code knowledge of python
    # triple-quoted-strings, but that is not sufficient to support the dynamic generation of new
    # phrases at runtime.
    #
    # Therefore, this compromise has been implemented. The presence of a line with one or more
    # triplets represents the beginning and end of a multi-line phrase. Indentation tracking will
    # pause when one of these lines is found and resume when another is encountered. Examples of
    # these triples are:
    #
    #       Enter Multiline Phrase  Exit Multiline Phrase
    #       ----------------------  ---------------------
    #                """                    """
    #                <<<                    >>>         !!! Note that the enter and exit triplets do not have to be the same
    #               <<<!!!                !!!>>>        !!! Note that there can be multiple triplets as part of a phrase
    #

    content = content if content and content[-1] == "\n" else (content + "\n")
    multiline_tokens_to_ignore = multiline_tokens_to_ignore or set()
    suppress_indentation_func = suppress_indentation_func or (lambda *args, **kwargs: False)

    content_length = len(content)

    # ----------------------------------------------------------------------
    @dataclass
    class IndentationInfo(object):
        num_chars: int
        value: int

    # ----------------------------------------------------------------------
    @dataclass
    class MultilineTokenInfo(object):
        line_index: int
        num_delimiters: int

    # ----------------------------------------------------------------------

    line_infos: List[LineInfo] = []
    indentation_stack: List[IndentationInfo] = [IndentationInfo(0, 0)]
    multiline_token_info: Optional[MultilineTokenInfo] = None

    offset = 0

    # ----------------------------------------------------------------------
    def CreateLineInfo() -> LineInfo:
        nonlocal offset
        nonlocal multiline_token_info

        # Get the extent of the line
        offset_begin = offset

        whitespace_ranges: List[OffsetRange] = []
        whitespace_start: Optional[int] = None

        while True:
            char = content[offset]

            if char == " " or char == "\t":
                if whitespace_start is None:
                    whitespace_start = offset

            else:
                if whitespace_start is not None:
                    whitespace_ranges.append(OffsetRange.Create(whitespace_start, offset))

                    whitespace_start = None

                if char == "\n":
                    break

            offset += 1

        offset_end = offset

        # Get the extent of the content
        if not whitespace_ranges:
            content_begin = offset_begin
            content_end = offset_end
        else:
            if whitespace_ranges[0].begin == offset_begin:
                content_begin = whitespace_ranges[0].end
            else:
                content_begin = offset_begin

            if whitespace_ranges[-1].end == offset_end and whitespace_ranges[-1].begin != offset_begin:
                content_end = whitespace_ranges[-1].begin
            else:
                content_end = offset_end

        # Calculate new dedentation- and indentation-values
        suppress_indentation = suppress_indentation_func(
            offset_begin,
            offset_end,
            content_begin,
            content_end,
        )

        if (
            content_begin == content_end
            or multiline_token_info is not None
            or suppress_indentation
        ):
            num_dedents = None
            new_indent_value = None

            if suppress_indentation:
                content_begin = offset_begin

        else:
            # Does the detected indentation for this line represent a dedent and/or indent?
            this_num_chars = content_begin - offset_begin
            this_indentation_value = 0

            if this_num_chars != 0:
                for index in range(offset_begin, content_begin):
                    char = content[index]

                    # Ensure that " \t" compares as different from "\t " and that "\t" compares
                    # as different from " ".
                    if char == " ":
                        this_indentation_value += 1
                    elif char == "\t":
                        this_indentation_value += (index - offset_begin + 1) * 100
                    else:
                        assert False, char  # pragma: no cover

            # Ensure that the whitespace prefix for this line uses the same configuration of tabs and
            # spaces as the indentation associated with the previous line if the number of characters
            # are the same.
            if (
                this_num_chars == indentation_stack[-1].num_chars
                and this_indentation_value != indentation_stack[-1].value
            ):
                raise InvalidTabsAndSpacesError.Create(
                    location=Location.Create(len(line_infos) + 1, content_begin - offset_begin + 1),
                )

            num_dedents = 0

            # Detect dedents
            while this_num_chars < indentation_stack[-1].num_chars:
                num_dedents += 1
                indentation_stack.pop()

            if num_dedents == 0:
                num_dedents = None

            # Detect indents
            if this_num_chars > indentation_stack[-1].num_chars:
                new_indent_value = this_indentation_value
                indentation_stack.append(IndentationInfo(this_num_chars, this_indentation_value))
            else:
                new_indent_value = None

        offset += 1

        return LineInfo.Create(
            offset_begin,
            offset_end,
            content_begin,
            content_end,
            whitespace_ranges,
            num_dedents,
            new_indent_value,
        )

    # ----------------------------------------------------------------------

    while offset < content_length:
        line_infos.append(CreateLineInfo())

        num_muliline_delimiters = GetNumMultilineTokenDelimiters(
            content,
            line_infos[-1].content_begin,
            line_infos[-1].content_end,
        )

        if (
            num_muliline_delimiters != 0
            and content[line_infos[-1].content_begin : line_infos[-1].content_end] not in multiline_tokens_to_ignore
        ):
            # Toggle the current state
            if multiline_token_info is None:
                multiline_token_info = MultilineTokenInfo(len(line_infos) - 1, num_muliline_delimiters)
            else:
                multiline_token_info = None

    # Detect when a multiline token has been opened but not closed
    if multiline_token_info is not None:
        line_info = line_infos[multiline_token_info.line_index]

        raise NoClosingMultilineTokenError.Create(
            location=Location.Create(multiline_token_info.line_index + 1, line_info.content_begin - line_info.offset_begin + 1),
        )

    # Add trailing dedents if necessary
    if len(indentation_stack) > 1:
        line_infos.append(
            LineInfo.Create(
                offset,
                offset,
                offset,
                offset,
                [],
                num_dedents=len(indentation_stack) - 1,
            ),
        )

    return NormalizedContent.Create(
        content,
        content_length,
        line_infos,
        None,  # type: ignore
    )
