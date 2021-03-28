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
from typing import List, Optional, Tuple

import CommonEnvironment

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

import Errors
import Tokens
import Utils

# ----------------------------------------------------------------------
Indentation                                 = namedtuple("Indentation", ["Value", "NumChars"])


# ----------------------------------------------------------------------
def Normalize(
    source_name: str,
    content: str,
) -> List[str]:
    """\
    Removes comments and converts multiline strings into single line-strings.

    In traditional parsers, a lexer can do these types of things inline while
    processing content. However, this parser combines the ideas of a lexer and
    parser and therefore must handle some of these activities before lexing can
    begin.
    """

    if content[-1] != "\n":
        content += "\n"

    len_content = len(content)
    offset = 0

    lines: List[str] = []
    indentations: List[Indentation] = []

    string_lines: Optional[List[Tuple[int, int]]] = None
    postprocess_string_lines = False

    line_start_offset = 0
    whitespace_length = 0
    comment_token_offset: Optional[int] = None

    while offset < len_content:
        char = content[offset]

        if whitespace_length is not None:
            if char == " ":
                whitespace_length += 1
            elif char == "\t":
                whitespace_length += 2
            else:
                assert char == "\n" or not char.isspace(), char

                indentations.append(Indentation(whitespace_length, offset - line_start_offset))
                whitespace_length = None

        if char == "\n":
            line_end_offset = offset

            if string_lines is not None:
                string_lines.append((line_start_offset, line_end_offset))

                if postprocess_string_lines:
                    # The string delimiters must have matching indentation levels.
                    if indentations[-1].Value != indentations[-1 * len(string_lines)].Value:
                        raise Errors.InvalidMultilineStringPrefixError(
                            source_name,
                            len(lines) + len(string_lines),
                            indentations[-1].NumChars + 1,
                        )

                    # All string content must be indented at least as much as the initial line
                    ref_indentation = indentations[-1]
                    string_content = []

                    for delta in range(1, len(string_lines) - 1):
                        whitespace_lengths_delta = -len(string_lines) + delta

                        this_indentation = indentations[whitespace_lengths_delta]

                        if (
                            string_lines[delta][0] != string_lines[delta][1]    # <Value 'string_lines' is unsubscriptable> pylint: disable=E1136
                            and this_indentation.Value < ref_indentation.Value
                        ):
                            raise Errors.InvalidMultilineStringPrefixError(
                                source_name,
                                len(lines) + delta + 1,
                                this_indentation.NumChars + 1,
                            )

                        string_content.append(
                            content[
                                string_lines[delta][0] + ref_indentation.NumChars   # <Value 'string_lines' is unsubscriptable> pylint: disable=E1136
                                : string_lines[delta][1]                            # <Value 'string_lines' is unsubscriptable> pylint: disable=E1136
                            ],
                        )

                        indentations[whitespace_lengths_delta] = Indentation(indentations[-1].Value, 0)

                    lines.append('"{}"'.format("\n".join(string_content).replace('"', '\\"')))
                    lines += [""] * (len(string_lines) - 1)

                    indentations[-1] = Indentation(indentations[-1].Value, 0)
                    indentations[-len(string_lines)] = Indentation(indentations[-1].Value, 0)

                    # Reset the state
                    string_lines = None
                    postprocess_string_lines = False
            else:
                # Capture the extent of the line without trailing comments
                if comment_token_offset is not None:
                    line_end_offset = comment_token_offset

                # Remove trailing whitespace
                while line_end_offset > line_start_offset and content[line_end_offset - 1].isspace():
                    line_end_offset -= 1

                lines.append(content[line_start_offset : line_end_offset])

            # Reset the state
            line_start_offset = offset + 1
            comment_token_offset = None
            whitespace_length = 0

        elif Utils.IsTokenMatch(
            content,
            Tokens.COMMENT_TOKEN,
            len_content=len_content,
            offset=offset,
        ):
            if comment_token_offset is None:
                comment_token_offset = offset

            offset += len(Tokens.COMMENT_TOKEN)
            continue

        elif Utils.IsTokenMatch(
            content,
            Tokens.MULTILINE_STRING_TOKEN,
            len_content=len_content,
            offset=offset,
        ):
            if (
                offset + len(Tokens.MULTILINE_STRING_TOKEN) >= len_content
                or content[offset + len(Tokens.MULTILINE_STRING_TOKEN)] != "\n"
            ):
                raise Errors.MissingMultilineTokenNewlineSuffixError(
                    source_name,
                    len(lines) + len(string_lines or []),
                    offset - line_start_offset + len(Tokens.MULTILINE_STRING_TOKEN) + 1,
                )

            if string_lines is None:
                # We are looking at an opening token
                string_lines = []
            else:
                # We are looking at a closing token
                postprocess_string_lines = True

            offset += len(Tokens.MULTILINE_STRING_TOKEN)
            continue

        offset += 1

    if string_lines is not None:
        raise Errors.MissingMultilineStringTerminatorError(
            source_name,
            len(lines) + 1,
            # The column will be the length of the first string line minus the length of the token
            string_lines[0][1] - string_lines[0][0] - len(Tokens.MULTILINE_STRING_TOKEN) + 1,
        )

    assert offset == line_start_offset, (offset, line_start_offset)

    return lines, indentations
