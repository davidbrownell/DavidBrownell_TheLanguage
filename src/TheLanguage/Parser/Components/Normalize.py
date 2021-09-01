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

from typing import cast, List, Optional, Set

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
@dataclass(frozen=True)
class NoClosingMultilineTokenError(Error):
    MessageTemplate                         = Interface.DerivedProperty("A closing token was not found to match this multi-line opening token.")


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
MULTILINE_PHRASE_TOKEN_LENGTH               = 3

def IsMultilinePhraseToken(
    content: str,
    start_index=0,
    end_index=None,
) -> bool:
    """See Comments in `Normalize`"""

    if end_index is None:
        end_index = len(content)

    if start_index == end_index:
        return False

    if (end_index - start_index) % MULTILINE_PHRASE_TOKEN_LENGTH != 0:
        return False

    while start_index != end_index:
        # The character must be a symbol
        if content[start_index].isalnum():
            return False

        for offset in range(start_index + 1, start_index + MULTILINE_PHRASE_TOKEN_LENGTH):
            if content[offset] != content[start_index]:
                return False

        start_index += MULTILINE_PHRASE_TOKEN_LENGTH

    return True


# ----------------------------------------------------------------------
def Normalize(
    content: str,

    # A set of tokens that look and feel like multi-line toggle tokens, but should not be considered
    # as such. An example of when to use this would be "---" when parsing yaml files.
    multiline_tokens_to_ignore: Optional[Set[str]]=None,

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
    #               <<<!!!                !!!>>>        !!! Note that there can be multiple triplets on the line
    #

    # ----------------------------------------------------------------------
    @dataclass
    class IndentationInfo(object):
        num_chars: int
        value: int

    # ----------------------------------------------------------------------

    if not content or content[-1] != "\n":
        content += "\n"

    len_content = len(content)

    line_infos: List[LineInfo] = []
    indentation_stack = [IndentationInfo(0, 0)]

    offset = 0
    multiline_token_opening_line_index: Optional[int] = None

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

                        if multiline_token_opening_line_index is None:
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

        if multiline_token_opening_line_index is None:
            num_dedents = num_dedents or None
        else:
            num_dedents = None
            new_indentation_value = None

        # <Too many positional arguments> pylint: disable=E1121
        return LineInfo(
            line_start_offset,
            line_end_offset,
            content_start_offset,
            content_end_offset,
            NumDedents=num_dedents,
            NewIndentationValue=new_indentation_value,
        )

    # ----------------------------------------------------------------------

    # Parse the content
    while offset < len_content:
        line_infos.append(CreateLineInfo())

        if (
            IsMultilinePhraseToken(
                content,
                start_index=line_infos[-1].PosStart,
                end_index=line_infos[-1].PosEnd,
            )
            and (
                multiline_tokens_to_ignore is None
                or content[line_infos[-1].PosStart : line_infos[-1].PosEnd] not in multiline_tokens_to_ignore
            )
        ):
            # Toggle the value
            if multiline_token_opening_line_index is None:
                multiline_token_opening_line_index = len(line_infos) - 1
            else:
                multiline_token_opening_line_index = None

    # Detect error when a multiline token has not been closed
    if multiline_token_opening_line_index is not None:
        index = cast(int, multiline_token_opening_line_index)
        line_info = line_infos[index]  # pylint: disable=invalid-sequence-index

        raise NoClosingMultilineTokenError(
            index + 1,
            line_info.PosStart - line_info.OffsetStart + 1,
        )

    # Add trailing dedents (if necessary)
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
