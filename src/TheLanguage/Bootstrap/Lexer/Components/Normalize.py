# ----------------------------------------------------------------------
# |
# |  Normalize.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 15:47:29
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
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

from dataclasses import dataclass, field

import CommonEnvironment
from CommonEnvironment import Interface
from CommonEnvironment import YamlRepr

from CommonEnvironmentEx.Package import InitRelativeImports

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

the_language_output_dir = os.getenv("THE_LANGUAGE_OUTPUT_DIR")
if the_language_output_dir is not None:
    import sys
    sys.path.insert(0, the_language_output_dir)
    from Lexer_TheLanguage.Components_TheLanguage.Normalize_TheLanguage import *
    sys.path.pop(0)

    USE_THE_LANGUAGE_GENERATED_CODE = True
else:
    USE_THE_LANGUAGE_GENERATED_CODE = False

    with InitRelativeImports():
        from ..Error import Error


    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class InvalidTabsAndSpacesError(Error):
        MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
            "The spaces and/or tabs used to indent this line differ from the spaces and/or tabs used on previous lines.",
        )


    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class NoClosingMultilineTokenError(Error):
        MessageTemplate                         = Interface.DerivedProperty(  # type: ignore
            "A closing token was not found to match this multi-line opening token.",
        )


    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class LineInfo(YamlRepr.ObjectReprImplBase):
        """Information about a single line"""

        OffsetStart: int
        OffsetEnd: int

        ContentStart: int
        ContentEnd: int

        NumDedents: Optional[int]               = field(default=None)
        NewIndentationValue: Optional[int]      = field(default=None)

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.OffsetStart >= 0, self
            assert self.OffsetEnd >= self.OffsetStart, self
            assert self.ContentStart >= self.OffsetStart, self
            assert self.ContentEnd  >= self.ContentStart, self
            assert self.ContentEnd <= self.OffsetEnd, self
            assert self.NumDedents is None or self.NumDedents > 0, self
            assert self.NewIndentationValue is None or self.NewIndentationValue > 0, self

        # ----------------------------------------------------------------------
        def HasWhitespacePrefix(self):
            return self.ContentStart != self.OffsetStart

        # ----------------------------------------------------------------------
        def HasContent(self):
            return self.ContentStart != self.ContentEnd

        # ----------------------------------------------------------------------
        def HasWhitespaceSuffix(self):
            return self.ContentEnd != self.OffsetEnd


    # ----------------------------------------------------------------------
    @dataclass(frozen=True, repr=False)
    class NormalizedContent(YamlRepr.ObjectReprImplBase):
        """"Data returned from calls to `Normalize`"""

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
                object.__setattr__(self, "Hash", self.__class__.CalculateHash(self.Content))

            YamlRepr.ObjectReprImplBase.__init__(
                self,
                Content=None,
                LineInfos=None,
                Hash=None,
            )

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
    # with `MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH` or `GetNumMultilineTokenDelimiters`.
    # ----------------------------------------------------------------------
    MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH       = 3

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


    # ----------------------------------------------------------------------
    # |
    # |  Public Functions
    # |
    # ----------------------------------------------------------------------
    def GetNumMultilineTokenDelimiters(
        content: str,
        start_index: int=0,
        end_index: Optional[int]=None,
    ) -> int:
        """\
        Returns the number of valid multiline token items at the given position in the provided content.

        See comments in `Normalize` for more information.
        """

        if end_index is None:
            end_index = len(content)

        if start_index == end_index:
            return 0

        if (end_index - start_index) % MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH != 0:
            return 0

        original_start_index = start_index

        while start_index != end_index:
            # The character must be a symbol
            if content[start_index].isalnum():
                return 0

            # Every item within the delimiter must be the same
            for offset in range(start_index + 1, start_index + MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH):
                if content[offset] != content[start_index]:
                    return 0

            start_index += MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH

        return (end_index - original_start_index) // MULTILINE_TOKEN_DELIMITER_ITEM_LENGTH


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
                    int,                        # offset_start
                    int,                        # offset_end
                    int,                        # content_start
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

        suppress_indentation_func = suppress_indentation_func or (lambda *args, **kwargs: False)

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

        if not content or content[-1] != "\n":
            content += "\n"

        if multiline_tokens_to_ignore is None:
            multiline_tokens_to_ignore = set()

        len_content = len(content)

        line_infos: List[LineInfo] = []
        indentation_stack: List[IndentationInfo] = [IndentationInfo(0, 0)]
        multiline_token_info: Optional[MultilineTokenInfo] = None

        offset = 0

        # TODO: Calculate whitespace upfront and store the info so that it doesn't have to be calculated over and over.

        # ----------------------------------------------------------------------
        def CreateLineInfo() -> LineInfo:
            nonlocal offset

            line_start_offset = offset
            line_end_offset: Optional[int] = None

            # TODO: There is likely a way to optimize the way in which indents/dedents are initially
            # committed and then reverted when suppress_indentation_func returns True.

            indentation_value: Optional[int] = 0
            new_indentation_value: Optional[int] = None
            popped_indentations: List[IndentationInfo] = []

            content_start_offset: Optional[int] = None
            content_end_offset: Optional[int] = None

            while offset < len_content:
                character = content[offset]

                if indentation_value is not None:
                    if character == " ":
                        indentation_value += 1
                    elif character == "\t":
                        # Ensure that " \t" compares as different from "\t " and that "\t" compares
                        # as different from " ".
                        indentation_value += (offset - line_start_offset + 1) * 100
                    else:
                        assert character == "\n" or not character.isspace(), character

                        num_chars = offset - line_start_offset

                        if character != "\n":
                            # Ensure that the whitespace prefix for this line use the same number of
                            # tabs and spaces as the indentation associated with the previous line.
                            if (
                                num_chars == indentation_stack[-1].num_chars
                                and indentation_value != indentation_stack[-1].value
                            ):
                                raise InvalidTabsAndSpacesError(
                                    len(line_infos) + 1,
                                    offset - line_start_offset + 1,
                                )

                            if multiline_token_info is None:
                                # Detect dedents
                                while num_chars < indentation_stack[-1].num_chars:
                                    popped_indentations.append(indentation_stack.pop())

                                # Detect indents
                                if num_chars > indentation_stack[-1].num_chars:
                                    indentation_stack.append(IndentationInfo(num_chars, indentation_value))
                                    new_indentation_value = indentation_value

                        indentation_value = None
                        content_start_offset = offset

                if character == "\n":
                    line_end_offset = offset
                    offset += 1

                    # Detect trailing whitespace
                    content_end_offset = line_end_offset

                    assert content_start_offset is not None
                    while content_end_offset > content_start_offset and content[content_end_offset - 1].isspace():
                        content_end_offset -= 1

                    break

                offset += 1

            assert line_end_offset is not None
            assert content_start_offset is not None
            assert content_end_offset is not None

            if multiline_token_info is None:
                # If here, we are not in the midst of a multi-line token. Is this indentation
                # information that should be suppressed?
                if (
                    (popped_indentations or new_indentation_value is not None)
                    and suppress_indentation_func(
                        line_start_offset,
                        line_end_offset,
                        content_start_offset,
                        content_end_offset,
                    )
                ):
                    if new_indentation_value is not None:
                        assert indentation_stack
                        indentation_stack.pop()

                        new_indentation_value = None
                        content_start_offset = line_start_offset

                    # Restore any popped indentations
                    indentation_stack.extend(popped_indentations)
                    popped_indentations = []

                num_dedents = len(popped_indentations) if popped_indentations else None

            else:
                # If here, we are in the midst of a multi-line token and all indentation information
                # should be ignored.
                num_dedents = None
                new_indentation_value = None

            # pylint: disable=too-many-function-args
            return LineInfo(
                line_start_offset,
                line_end_offset,
                content_start_offset,
                content_end_offset,
                NumDedents=num_dedents,
                NewIndentationValue=new_indentation_value,
            )

        # ----------------------------------------------------------------------

        while offset < len_content:
            line_infos.append(CreateLineInfo())

            num_multiline_delimiters = GetNumMultilineTokenDelimiters(
                content,
                start_index=line_infos[-1].ContentStart,
                end_index=line_infos[-1].ContentEnd,
            )

            if (
                num_multiline_delimiters != 0
                and content[line_infos[-1].ContentStart : line_infos[-1].ContentEnd] not in multiline_tokens_to_ignore
            ):
                # Toggle the current state
                if multiline_token_info is None:
                    multiline_token_info = MultilineTokenInfo(len(line_infos) - 1, num_multiline_delimiters)
                elif num_multiline_delimiters == multiline_token_info.num_delimiters:
                    multiline_token_info = None

        # Detect when a multiline token has been opened but not closed
        if multiline_token_info is not None:
            line_info = line_infos[multiline_token_info.line_index]

            raise NoClosingMultilineTokenError(
                multiline_token_info.line_index + 1,
                line_info.ContentStart - line_info.OffsetStart + 1,
            )

        # Add trailing dedents if necessary
        if len(indentation_stack) > 1:
            line_infos.append(
                # pylint: disable=too-many-function-args
                LineInfo(
                    offset,
                    offset,
                    offset,
                    offset,
                    NumDedents=len(indentation_stack) - 1,
                ),
            )

        # pylint: disable=too-many-function-args
        return NormalizedContent(content, len_content, line_infos)
