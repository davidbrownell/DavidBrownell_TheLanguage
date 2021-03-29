# ----------------------------------------------------------------------
# |
# |  Normalize.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-03-27 10:31:07
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Contains types that facilitate the tokenization process"""

import os

from collections import namedtuple
from typing import List, Optional

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

import Errors
import Tokens
import Utils

# ----------------------------------------------------------------------
NormalizedLine                              = namedtuple("NormalizedLine", ["Value", "Indentation"])

# ----------------------------------------------------------------------
def Normalize(
    source_name: str,
    content: str,
) -> List[NormalizedLine]:
    """\
    Removes comments and converts multiline strings into single line-strings.

    In traditional parsers, a lexer can do these types of things inline while
    processing content. However, this parser combines the ideas of a lexer and
    parser and therefore must handle some of these activities before lexing can
    begin.
    """

    if content[-1] != "\n":
        content += "\n"

    # ----------------------------------------------------------------------
    StringLineInfo                          = namedtuple("StringLineInfo", ["StartOffset", "EndOffset", "Indentation", "NumIndentationChars"])

    # ----------------------------------------------------------------------

    len_content = len(content)
    offset = 0

    lines: List[NormalizedLine] = []

    string_line_infos: List[StringLineInfo] = []
    process_string_lines = False

    # ----------------------------------------------------------------------
    def GenerateLine():
        nonlocal offset
        nonlocal string_line_infos
        nonlocal process_string_lines

        line_start_offset = offset

        indentation_value: Optional[int] = None
        indentation_value_calc = 0
        indentation_chars = 0

        comment_token_offset = None

        while offset < len_content:
            char = content[offset]

            if indentation_value is None:
                if char == " ":
                    indentation_value_calc += 1
                elif char == "\t":
                    indentation_value_calc += 2
                else:
                    assert char == "\n" or not char.isspace(), char

                    indentation_value = indentation_value_calc
                    indentation_chars = offset - line_start_offset

            if char == "\n":
                line_end_offset = offset
                offset += 1

                # If we aren't looking at string content...
                if not string_line_infos and not process_string_lines:
                    # Capture the extent of the line without trailing comments
                    if comment_token_offset is not None:
                        line_end_offset = comment_token_offset

                    # Remove trailing whitespace
                    while line_end_offset > line_start_offset and content[line_end_offset - 1].isspace():
                        line_end_offset -= 1

                    return [
                        NormalizedLine(content[line_start_offset + indentation_chars : line_end_offset], indentation_value),
                    ]

                # If here, we are looking at string content...
                string_line_infos.append(
                    StringLineInfo(
                        line_start_offset,
                        line_end_offset,
                        indentation_value,
                        indentation_chars,
                    ),
                )

                # Nothing to do if we are still processing the string lines
                if process_string_lines:
                    return []

                assert len(string_line_infos) >= 2, string_line_infos

                # The string delimiters must have matching indentation levels
                if string_line_infos[0].Indentation != string_line_infos[-1].Indentation:
                    raise Errors.InvalidMultilineStringPrefixError(
                        source_name,
                        len(lines) + len(string_line_infos),
                        string_line_infos[-1].NumIndentationChars + 1,
                    )

                # All string content must be indented at least as much as the delimiters
                ref_string_info = string_line_infos[0]
                string_content = []

                for delta in range(1, len(string_line_infos) - 1):
                    this_string_info = string_line_infos[delta]

                    if (
                        this_string_info.EndOffset != this_string_info.StartOffset
                        and this_string_info.Indentation < ref_string_info.Indentation
                    ):
                        raise Errors.InvalidMultilineStringPrefixError(
                            source_name,
                            len(lines) + delta + 1,
                            this_string_info.NumIndentationChars + 1,
                        )

                    string_content.append(
                        content[
                            this_string_info.StartOffset + ref_string_info.NumIndentationChars
                            : this_string_info.EndOffset
                        ],
                    )

                indentation = string_line_infos[0].Indentation
                num_empty_lines = len(string_line_infos) - 1

                string_line_infos = []

                return [
                    NormalizedLine('"{}"'.format("\n".join(string_content).replace('"', '\\"')), indentation),
                ] + ([NormalizedLine("", indentation)] * num_empty_lines)

            elif Utils.IsTokenMatch(
                content,
                Tokens.COMMENT_TOKEN,                   # <Module 'Tokens' has no '___' member> pylint: disable=E1101
                offset=offset,
                len_content=len_content,
                len_token=Tokens.COMMENT_TOKEN_length,  # <Module 'Tokens' has no '___' member> pylint: disable=E1101
            )[0]:
                if comment_token_offset is None:
                    comment_token_offset = offset

                offset += Tokens.COMMENT_TOKEN_length   # <Module 'Tokens' has no '___' member> pylint: disable=E1101
                continue

            elif Utils.IsTokenMatch(
                content,
                Tokens.MULTILINE_STRING_TOKEN,                              # <Module 'Tokens' has no '___' member> pylint: disable=E1101
                offset=offset,
                len_content=len_content,
                len_token=Tokens.MULTILINE_STRING_TOKEN_length,             # <Module 'Tokens' has no '___' member> pylint: disable=E1101
            )[0]:
                if (
                    offset + Tokens.MULTILINE_STRING_TOKEN_length >= len_content        # <Module 'Tokens' has no '___' member> pylint: disable=E1101
                    or content[offset + Tokens.MULTILINE_STRING_TOKEN_length] != "\n"   # <Module 'Tokens' has no '___' member> pylint: disable=E1101
                ):
                    raise Errors.MissingMultilineTokenNewlineSuffixError(
                        source_name,
                        len(lines) + len(string_line_infos or []),
                        offset - line_start_offset + Tokens.MULTILINE_STRING_TOKEN_length + 1,  # <Module 'Tokens' has no '___' member> pylint: disable=E1101
                    )

                process_string_lines = not process_string_lines

                offset += Tokens.MULTILINE_STRING_TOKEN_length              # <Module 'Tokens' has no '___' member> pylint: disable=E1101
                continue

            offset += 1

        return []

    # ----------------------------------------------------------------------

    while offset < len_content:
        lines += GenerateLine()

    if string_line_infos:
        raise Errors.MissingMultilineStringTerminatorError(
            source_name,
            len(lines) + 1,
            # The column will be the length of the first string line minus the length of the token
            string_line_infos[0].EndOffset - string_line_infos[0].StartOffset - Tokens.MULTILINE_STRING_TOKEN_length + 1,   # <Module 'Tokens' has no '___' member> pylint: disable=E1101
        )

    return lines
